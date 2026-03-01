import re
import requests
import json
import gzip
from datetime import datetime, timezone, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for older Python versions if needed, though we know it's 3.12
    ZoneInfo = None
from colorama import Fore
from .models import Alert, AlertStatus, ThreatType, CATEGORY_TO_STATUS, CATEGORY_TO_THREAT_TYPE, THREAT_PATTERNS

# Define Israel Timezone (UTC+2 standard, UTC+3 DST)
# For simplicity, we can use a fixed offset if pytz/zoneinfo isn't available,
# but it's better to use pytz or handle DST if possible.
# Since we don't have pytz guaranteed, we'll try to use a simple offset or just treat as UTC and let the consumer handle display.
# However, the user wants the parser to fix it.
# Let's assume the system time is configured correctly and use `astimezone()`.

class OrefAlertParser:
    def __init__(self, alerts_data):
        if isinstance(alerts_data, str):
            self.alerts_data = json.loads(alerts_data)
        else:
            self.alerts_data = alerts_data
        self.alerts = self._categorize_alerts()
        self.alerts = self._deduplicate_alerts()

    def _parse_alert(self, alert):
        """Converts a single Pikud Haoref alert dict to an Alert object with resolved status and threat type."""
        oref_category = alert.get("category")
        title = alert.get("title", "")
        if not title and "title" in alert:
            title = alert["title"]
            
        # For the new GetAlarmsHistory.aspx endpoint, the description is in category_desc
        # and title might be missing.
        category_desc = alert.get("category_desc")
        if not title and category_desc:
            title = category_desc
            
        status = CATEGORY_TO_STATUS.get(oref_category)
        threat_type = CATEGORY_TO_THREAT_TYPE.get(oref_category)

        raw_date = alert.get("alertDate")
        
        # Real-time alerts format has `cat` instead of `category`
        if oref_category is None and "cat" in alert:
            try:
                oref_category = int(alert["cat"])
                status = CATEGORY_TO_STATUS.get(oref_category)
                threat_type = CATEGORY_TO_THREAT_TYPE.get(oref_category)
            except ValueError:
                pass
            
        # Real-time alerts might not have `alertDate`, so default to current UTC time if missing
        if raw_date is None and "id" in alert:
            # We use UTC for real-time alerts created on the fly
            raw_date = datetime.now(timezone.utc)
            
        alert_date_obj = None
        if isinstance(raw_date, str):
            try:
                # The API provides dates in "YYYY-MM-DD HH:MM:SS" format in Israel time.
                # We should NOT mark it as UTC if it's already local time.
                if "T" in raw_date:
                    alert_date_obj = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
                else:
                    alert_date_obj = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
                
                # Since the API data is in Israel time, we attach the Israel timezone.
                # This correctly handles standard/daylight savings time.
                try:
                    if ZoneInfo:
                        alert_date_obj = alert_date_obj.replace(tzinfo=ZoneInfo("Asia/Jerusalem"))
                    else:
                        raise ImportError
                except Exception:
                    # Fallback to fixed offset if ZoneInfo or the specific zone is not available
                    # Note: We use a fixed offset of +2. This is correct for most of the year.
                    # For a production app on Windows without tzdata, we might need a better way,
                    # but this fixes the immediate double-offset bug.
                    israel_tz = timezone(timedelta(hours=2))
                    alert_date_obj = alert_date_obj.replace(tzinfo=israel_tz)
            except (ValueError, TypeError):
                # In case of format errors or if raw_date is None, leave it as None.
                alert_date_obj = None
        elif isinstance(raw_date, datetime):
            # If it's already a datetime object (like from datetime.now(timezone.utc)), use it.
            alert_date_obj = raw_date

        # The category for ended alerts can be inconsistent. A reliable way to identify
        # them is by checking for "ended" ("הסתיים" or "הסתיימה") in the title.
        if "הסתיים" in title or "הסתיימה" in title:
            status = AlertStatus.ENDED
            
            # For ended alerts, the threat type must be parsed from the title,
            # as the category might not be informative.
            threat_type_from_title = None
            for ttype, pattern in THREAT_PATTERNS.items():
                if pattern.search(title):
                    threat_type_from_title = ttype
                    break
            
            if threat_type_from_title:
                threat_type = threat_type_from_title
            else:
                # If it's an ended alert but we can't determine the type, it's an error.
                raise ValueError(f"Unexpected ended alert type: {title}")

        return Alert(
            alertDate=alert_date_obj,
            title=title,
            location=alert.get("data", []),
            oref_category=oref_category,
            status=status,
            threat_type=threat_type,
            message=alert.get("category_desc")
        )

    def _categorize_alerts(self):
        """Converts all alerts to Alert objects with status and threat_type fields."""
        return [self._parse_alert(alert) for alert in self.alerts_data]

    def _deduplicate_alerts(self) -> list[Alert]:
        """Removes duplicate alerts based on location, threat_type, and rounded alertDate."""
        seen = set()
        unique_alerts = []
        for alert in self.alerts:
            # Use a tuple of (location, threat_type, rounded_time) as a unique key
            # Handle location being a list
            loc_key = tuple(alert.location) if isinstance(alert.location, list) else alert.location
            key = (
                loc_key,
                alert.threat_type,
                str(alert.status),
                str(alert.title),
                str(alert.oref_category),
                str(alert.alertDate)[:16]  # e.g., up to minute
            )
            if key not in seen:
                seen.add(key)
                unique_alerts.append(alert)
        return unique_alerts

    def get_alerts(self):
        return self.alerts


def filter_alerts_by_location(alerts: list[Alert], locations: list[str]) -> list[Alert]:
    """
    Filters alerts by location.

    Args:
        alerts: A list of Alert objects.
        locations: A list of location names to filter by.

    Returns:
        A new list of alerts that match the given locations.
    """
    if not locations:
        return []
    
    location_set = {loc.lower() for loc in locations}
    
    filtered_alerts = []
    for alert in alerts:
        if not alert.location:
            continue
            
        if isinstance(alert.location, list):
            # If location is a list, check if ANY of the locations match
            # This logic assumes we want to show the alert if the requested location is involved.
            if any(loc.lower() in location_set for loc in alert.location):
                filtered_alerts.append(alert)
        elif isinstance(alert.location, str):
            if alert.location.lower() in location_set:
                filtered_alerts.append(alert)
                
    return filtered_alerts


def get_cities_from_alerts(alerts: list[Alert]) -> list[str]:
    """Extracts a unique list of cities from a list of alerts."""
    cities = set()
    for alert in alerts:
        if alert.location:
            cities.add(alert.location)
    return list(cities)


def save_alerts(alerts, filename="alerts.json"):
    """Saves alert data to a JSON file."""
    if alerts:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([alert.to_dict() for alert in alerts], f, ensure_ascii=False, indent=4)
        print(f"Alerts saved to {filename}")


def display_alerts(alerts):
    """Displays alerts grouped by status and threat type."""
    for status in AlertStatus:
        print(f"--- {status.value.capitalize()} Alerts ---")
        filtered = [a for a in alerts if a.status == status]
        if filtered:
            for alert in filtered:
                color = Fore.RESET
                if status == AlertStatus.ACTIVE:
                    color = Fore.RED
                elif status == AlertStatus.UPCOMING:
                    color = Fore.YELLOW
                elif status == AlertStatus.ENDED:
                    color = Fore.LIGHTBLACK_EX
                print(color + f"Time: {alert.alertDate}, Location: {alert.location}, Type: {alert.threat_type.value if alert.threat_type else 'Unknown'}")
        else:
            print(f"No {status.value} alerts.")
        print(Fore.RESET)


def fetch_alerts():
    """
    Fetches alert data from the oref.org.il API, handling potential compression
    and JSON decoding issues.
    """
    url = "https://alerts-history.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&mode=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36',
        'Referer': 'https://www.oref.org.il/heb/alerts-history',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'Accept': 'application/json, text/plain, */*',
    }
    try:
        # Use stream=True to handle the raw response and avoid issues with
        # incorrect Content-Length headers.
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        # Read the raw bytes from the stream, which gives us the complete response.
        raw_content = response.raw.read()
        
        try:
            decompressed_content = raw_content
            # The 'Content-Encoding' header is a hint, but the content itself is the truth.
            # We attempt to decompress if the header is present.
            if response.headers.get('Content-Encoding') == 'gzip':
                try:
                    decompressed_content = gzip.decompress(raw_content)
                except (gzip.BadGzipFile, OSError):
                    # If decompression fails, assume it's not actually gzipped.
                    # The server sometimes sends the header incorrectly.
                    pass
            
            # The API may send a UTF-8 BOM, which json.loads doesn't handle.
            # 'utf-8-sig' will correctly decode the content, stripping the BOM if present.
            json_text = decompressed_content.decode('utf-8-sig')
            return json.loads(json_text)

        except json.JSONDecodeError:
            print("Error: Malformed JSON response from the API.")
            print(f"Response Headers: {response.headers}")
            print(f"Actual Content Length (raw bytes): {len(raw_content)}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []


def fetch_realtime_alerts():
    """
    Fetches real-time alert data from the oref.org.il API.
    This endpoint is optimized for high-frequency polling.
    Returns an empty list if no alerts are active.
    """
    url = "https://www.oref.org.il/warningMessages/alert/Alerts.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36',
        'Referer': 'https://www.oref.org.il/',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'Accept': 'application/json, text/plain, */*',
        'X-Requested-With': 'XMLHttpRequest'
    }
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        raw_content = response.raw.read()

        # Handle empty response (no alerts)
        if not raw_content or raw_content.strip() == b"":
             return []

        try:
            decompressed_content = raw_content
            if response.headers.get('Content-Encoding') == 'gzip':
                try:
                    decompressed_content = gzip.decompress(raw_content)
                except (gzip.BadGzipFile, OSError):
                    pass
            
            # Decode and parse
            # The real-time endpoint might return a single object or a list.
            # Oref often returns a flat list or a single object if there's only one.
            # Let's standardize to a list.
            json_text = decompressed_content.decode('utf-8-sig')
            
            if not json_text.strip():
                return []

            data = json.loads(json_text)
            
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                return []

        except json.JSONDecodeError:
            # If it's not valid JSON but we got content, log it but return empty
            # Sometimes 404s or error pages sneak through as 200s
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error fetching real-time data: {e}")
        return []


def process_alerts():
    """Main function to fetch, save, and display alerts."""
    alerts_data = fetch_alerts()
    if alerts_data:
        parser = OrefAlertParser(alerts_data)
        alerts = parser.get_alerts()
        save_alerts(alerts)
        display_alerts(alerts)
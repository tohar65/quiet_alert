import re
import requests
import json
import gzip
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Union, List, Dict
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for older Python versions if needed, though we know it's 3.12
    ZoneInfo = None
from colorama import Fore
from .models import Alert, AlertStatus, ThreatType, CATEGORY_TO_STATUS, CATEGORY_TO_THREAT_TYPE, THREAT_PATTERNS

class OrefAlertParser:
    """
    Parser for Pikud Haoref (Home Front Command) alert data.

    This class handles converting raw JSON data from Oref APIs into structured Alert objects,
    performing categorization, timezone normalization, and deduplication.
    """

    def __init__(self, alerts_data: Union[str, List[Dict[str, Any]]]):
        """
        Initializes the parser with raw alert data.

        Args:
            alerts_data: Either a JSON string or a list of dictionaries representing raw alerts.
        """
        if isinstance(alerts_data, str):
            self.alerts_data = json.loads(alerts_data)
        else:
            self.alerts_data = alerts_data
        self.alerts: List[Alert] = self._categorize_alerts()
        self.alerts = self._deduplicate_alerts()

    def _parse_alert(self, alert: Dict[str, Any]) -> Alert:
        """
        Converts a single Pikud Haoref alert dict to an Alert object.

        Resolves the status and threat type based on Oref category and title content.

        Args:
            alert: A dictionary containing raw alert data from the Oref API.

        Returns:
            An Alert object with normalized fields.

        Raises:
            ValueError: If an ended alert type cannot be determined from the title.
        """
        # Extract initial values
        oref_category_raw = alert.get("category")
        if oref_category_raw is None:
            oref_category_raw = alert.get("cat")
            
        oref_category: Optional[int] = None
        if oref_category_raw is not None:
            try:
                oref_category = int(oref_category_raw)
            except (ValueError, TypeError):
                pass

        title = alert.get("title", "")
        if not title and "title" in alert:
            title = alert["title"]
            
        category_desc = alert.get("category_desc")
        if not title and category_desc:
            title = category_desc
            
        status = CATEGORY_TO_STATUS.get(oref_category) if oref_category is not None else None
        threat_type = CATEGORY_TO_THREAT_TYPE.get(oref_category) if oref_category is not None else None

        raw_date = alert.get("alertDate")
        
        # Real-time alerts might not have `alertDate`, so default to current UTC time if missing
        if raw_date is None and "id" in alert:
            raw_date = datetime.now(timezone.utc)
            
        alert_date_obj = None
        if isinstance(raw_date, str):
            try:
                if "T" in raw_date:
                    alert_date_obj = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
                else:
                    alert_date_obj = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
                
                try:
                    if ZoneInfo:
                        alert_date_obj = alert_date_obj.replace(tzinfo=ZoneInfo("Asia/Jerusalem"))
                    else:
                        raise ImportError
                except Exception:
                    israel_tz = timezone(timedelta(hours=2))
                    alert_date_obj = alert_date_obj.replace(tzinfo=israel_tz)
            except (ValueError, TypeError):
                alert_date_obj = None
        elif isinstance(raw_date, datetime):
            alert_date_obj = raw_date

        # Refine status and threat type for ended alerts
        if title and ("הסתיים" in title or "הסתיימה" in title):
            status = AlertStatus.ENDED
            
            threat_type_from_title = None
            for ttype, pattern in THREAT_PATTERNS.items():
                if pattern.search(title):
                    threat_type_from_title = ttype
                    break
            
            if threat_type_from_title:
                threat_type = threat_type_from_title
            else:
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

    def _categorize_alerts(self) -> List[Alert]:
        """
        Converts all raw alerts to Alert objects.

        Returns:
            A list of structured Alert objects.
        """
        return [self._parse_alert(alert) for alert in self.alerts_data]

    def _deduplicate_alerts(self) -> List[Alert]:
        """
        Removes duplicate alerts.

        Duplicates are identified based on location, threat_type, status, title,
        category, and alertDate (rounded to the minute).

        Returns:
            A list of unique Alert objects.
        """
        seen = set()
        unique_alerts = []
        for alert in self.alerts:
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

    def get_alerts(self) -> List[Alert]:
        """
        Returns the parsed and deduplicated alerts.

        Returns:
            A list of Alert objects.
        """
        return self.alerts


def filter_alerts_by_location(alerts: List[Alert], locations: List[str]) -> List[Alert]:
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
            if any(loc.lower() in location_set for loc in alert.location):
                filtered_alerts.append(alert)
        elif isinstance(alert.location, str):
            if alert.location.lower() in location_set:
                filtered_alerts.append(alert)
                
    return filtered_alerts


def get_cities_from_alerts(alerts: List[Alert]) -> List[str]:
    """
    Extracts a unique list of cities from a list of alerts.

    Args:
        alerts: A list of Alert objects.

    Returns:
        A list of unique city/location names.
    """
    cities = set()
    for alert in alerts:
        if alert.location:
            if isinstance(alert.location, list):
                for loc in alert.location:
                    cities.add(loc)
            else:
                cities.add(alert.location)
    return list(cities)


def save_alerts(alerts: List[Alert], filename: str = "alerts.json") -> None:
    """
    Saves alert data to a JSON file.

    Args:
        alerts: A list of Alert objects to save.
        filename: The path to the file where alerts should be saved.
    """
    if alerts:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([alert.to_dict() for alert in alerts], f, ensure_ascii=False, indent=4)
        print(f"Alerts saved to {filename}")


def display_alerts(alerts: List[Alert]) -> None:
    """
    Displays alerts grouped by status and threat type to the console.

    Args:
        alerts: A list of Alert objects to display.
    """
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


def fetch_alerts(url: Optional[str] = None, user_agent: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches alert history data from the oref.org.il API.

    Handles potential compression and JSON decoding issues, including UTF-8 BOM.

    Args:
        url: The URL to fetch from. If None, uses default Oref history URL.
        user_agent: The User-Agent to use. If None, uses default.

    Returns:
        A list of dictionaries representing raw alerts. Returns an empty list on failure.
    """
    if url is None:
        url = "https://alerts-history.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&mode=1"
    
    headers = {
        'User-Agent': user_agent or 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36',
        'Referer': 'https://www.oref.org.il/heb/alerts-history',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'Accept': 'application/json, text/plain, */*',
    }
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()

        raw_content = response.raw.read()
        
        try:
            decompressed_content = raw_content
            if response.headers.get('Content-Encoding') == 'gzip':
                try:
                    decompressed_content = gzip.decompress(raw_content)
                except (gzip.BadGzipFile, OSError):
                    pass
            
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


def fetch_realtime_alerts(url: Optional[str] = None, user_agent: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches real-time alert data from the oref.org.il API.

    This endpoint is optimized for high-frequency polling.

    Args:
        url: The URL to fetch from. If None, uses default Oref realtime URL.
        user_agent: The User-Agent to use. If None, uses default.

    Returns:
        A list of dictionaries representing active alerts. Returns an empty list if no alerts are active.
    """
    if url is None:
        url = "https://www.oref.org.il/warningMessages/alert/Alerts.json"
        
    headers = {
        'User-Agent': user_agent or 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36',
        'Referer': 'https://www.oref.org.il/',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'Accept': 'application/json, text/plain, */*',
        'X-Requested-With': 'XMLHttpRequest'
    }
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()

        raw_content = response.raw.read()

        if not raw_content or raw_content.strip() == b"":
             return []

        try:
            decompressed_content = raw_content
            if response.headers.get('Content-Encoding') == 'gzip':
                try:
                    decompressed_content = gzip.decompress(raw_content)
                except (gzip.BadGzipFile, OSError):
                    pass
            
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
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error fetching real-time data: {e}")
        return []


def process_alerts() -> None:
    """
    Main function to fetch, save, and display alerts.
    """
    alerts_data = fetch_alerts()
    if alerts_data:
        parser = OrefAlertParser(alerts_data)
        alerts = parser.get_alerts()
        save_alerts(alerts)
        display_alerts(alerts)

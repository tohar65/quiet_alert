import re
import requests
import json
import gzip
from datetime import datetime
from colorama import Fore
from .models import Alert, AlertStatus, ThreatType, CATEGORY_TO_STATUS, CATEGORY_TO_THREAT_TYPE, THREAT_PATTERNS


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
        status = CATEGORY_TO_STATUS.get(oref_category)
        threat_type = CATEGORY_TO_THREAT_TYPE.get(oref_category)

        raw_date = alert.get("alertDate")
        alert_date_obj = None
        if isinstance(raw_date, str):
            try:
                # The API provides dates in "YYYY-MM-DD HH:MM:SS" format.
                alert_date_obj = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                # In case of format errors or if raw_date is None, leave it as None.
                alert_date_obj = None
        elif isinstance(raw_date, datetime):
            # If it's already a datetime object, use it directly.
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
            location=alert.get("data"),
            oref_category=oref_category,
            status=status,
            threat_type=threat_type
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
            key = (
                alert.location,
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
    
    filtered_alerts = [
        alert for alert in alerts
        if alert.location and alert.location.lower() in location_set
    ]
    
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
    """Fetches alert data from the oref.org.il API."""
    url = "https://www.oref.org.il/WarningMessages/alert/History/AlertsHistory.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.oref.org.il/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        raw_content = response.content
        try:
            if response.headers.get('Content-Encoding') == 'gzip':
                # Only decompress if content starts with gzip magic number
                if raw_content[:2] == b'\x1f\x8b':
                    decompressed_content = gzip.decompress(raw_content)
                    json_data = json.loads(decompressed_content.decode('utf-8'))
                else:
                    # Content is not actually gzipped, just parse as JSON
                    json_data = response.json()
            else:
                # No compression header, parse as plain JSON.
                json_data = response.json()
            return json_data
        except json.JSONDecodeError:
            print("Error: Malformed JSON response from the API.")
            print(f"Response Headers: {response.headers}")
            print(f"Content-Length Header: {response.headers.get('Content-Length')}")
            print(f"Actual Content Length (raw bytes): {len(raw_content)}")
            print(f"Actual Content Length (decoded text): {len(response.text)}")
            print("Response Text (first 500 chars):")
            print(response.text[:500])
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def process_alerts():
    """Main function to fetch, save, and display alerts."""
    alerts_data = fetch_alerts()
    if alerts_data:
        parser = OrefAlertParser(alerts_data)
        alerts = parser.get_alerts()
        save_alerts(alerts)
        display_alerts(alerts)
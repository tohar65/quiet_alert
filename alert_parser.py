import re
import requests
import json
from datetime import datetime
from colorama import Fore
from alert_types import Alert, AlertStatus, ThreatType, CATEGORY_TO_STATUS, CATEGORY_TO_THREAT_TYPE, THREAT_PATTERNS


def get_key_by_value(d, value):
    return next((k for k, v in d.items() if v == value), None)


def parse_alert(alert):
    """Converts a single Pikud Haoref alert dict to an Alert object with resolved status and threat type."""
    oref_category = alert.get("category")
    title = alert.get("title", "")
    status = CATEGORY_TO_STATUS.get(oref_category)
    threat_type = CATEGORY_TO_THREAT_TYPE.get(oref_category)

    if get_key_by_value(CATEGORY_TO_STATUS, AlertStatus.ENDED) == oref_category:
        for ttype, pattern in THREAT_PATTERNS.items():
            if pattern.search(title):
                threat_type = ttype
                break
        else:
            raise ValueError(f"Unexpected ended alert type: {title}")

    return Alert(
        alertDate=alert.get("alertDate"),
        title=title,
        location=alert.get("data"),
        oref_category=oref_category,
        status=status,
        threat_type=threat_type
    )


def categorize_alerts(alerts):
    """Converts all alerts to Alert objects with status and threat_type fields."""
    return [parse_alert(alert) for alert in alerts]


def save_alerts(alerts, filename="alerts.json"):
    """Saves alert data to a JSON file."""
    if alerts:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([alert.to_dict() for alert in alerts], f, ensure_ascii=False, indent=4)
        print(f"Alerts saved to {filename}")


def log_alerts(log_file, alerts):
    """Logs the alerts to a file, grouped by status and threat type, with all alert fields in clear format."""
    with open(log_file, 'w', encoding='utf-8') as f:
        for status in AlertStatus:
            f.write(f"--- {status.value.capitalize()} Alerts ---\n")
            filtered = [a for a in alerts if a.status == status]
            if filtered:
                for alert in filtered:
                    f.write(f"Time: {alert.alertDate}\n")
                    f.write(f"Title: {alert.title}\n")
                    f.write(f"Location: {alert.location}\n")
                    f.write(f"Oref Category: {alert.oref_category}\n")
                    f.write(f"Status: {alert.status.value if alert.status else 'Unknown'}\n")
                    f.write(f"Threat Type: {alert.threat_type.value if alert.threat_type else 'Unknown'}\n")
                    f.write("-" * 40 + "\n")
            else:
                f.write(f"No {status.value} alerts.\n")
            f.write("\n")


def display_alerts(alerts, log_file=None):
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
    if log_file:
        log_alerts(log_file, alerts)
        print(f"\nResults logged to {log_file}")


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
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def process_alerts(log_file="alerts.log"):
    """Main function to fetch, save, and display alerts."""
    alerts_data = fetch_alerts()
    if alerts_data:
        alerts = categorize_alerts(alerts_data)
        save_alerts(alerts)
        display_alerts(alerts, log_file)
import re
import requests
import json
from datetime import datetime
from colorama import Fore

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

def save_alerts(data, filename="alerts.json"):
    """Saves alert data to a JSON file."""
    if data:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Alerts saved to {filename}")

def log_alerts(log_file, active_alerts, upcoming_alerts, aircraft_intrusion_alerts, ended_alerts, unexpected_alerts):
    """Logs the alerts to a file."""
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("--- Rocket Alerts ---\n")
        if active_alerts:
            for alert in active_alerts:
                alert_time = alert.get("alertDate", "N/A")
                city = alert.get("data", "N/A")
                f.write(f"Time: {alert_time}, Location: {city}, Type: Active\n")
        else:
            f.write("No active rocket alerts.\n")

        f.write("\n--- Upcoming Alerts ---\n")
        if upcoming_alerts:
            for alert in upcoming_alerts:
                alert_time = alert.get("alertDate", "N/A")
                city = alert.get("data", "N/A")
                f.write(f"Time: {alert_time}, Location: {city}, Type: Upcoming\n")
        else:
            f.write("No upcoming alerts.\n")

        f.write("\n--- Aircraft Intrusion Alerts ---\n")
        if aircraft_intrusion_alerts:
            for alert in aircraft_intrusion_alerts:
                alert_time = alert.get("alertDate", "N/A")
                city = alert.get("data", "N/A")
                title = re.sub(r'\s+', ' ', alert.get("title", "N/A")).strip()
                f.write(f"Time: {alert_time}, Location: {city}, Type: {title}\n")
        else:
            f.write("No aircraft intrusion alerts.\n")

        f.write("\n--- Ended Alerts ---\n")
        if ended_alerts:
            for alert in ended_alerts:
                alert_time = alert.get("alertDate", "N/A")
                city = alert.get("data", "N/A")
                title = re.sub(r'\s+', ' ', alert.get("title", "N/A")).strip()
                f.write(f"Time: {alert_time}, Location: {city}\n")
                f.write(f"  Type: {title}\n")
        else:
            f.write("No ended alerts.\n")

        if unexpected_alerts:
            f.write("\n--- Unexpected Alerts ---\n")
            for alert in unexpected_alerts:
                alert_time = alert.get("alertDate", "N/A")
                city = alert.get("data", "N/A")
                title = re.sub(r'\s+', ' ', alert.get("title", "N/A")).strip()
                f.write(f"Warning: Unexpected alert type: '{title}'\n")
                f.write(f"  Time: {alert_time}, Location: {city}\n")

def display_alerts(active_alerts, upcoming_alerts, aircraft_intrusion_alerts, ended_alerts, unexpected_alerts, log_file=None):
    """Displays active, upcoming, aircraft intrusion, ended, and unexpected alerts."""
    print("--- Rocket Alerts ---")
    if active_alerts:
        for alert in active_alerts:
            alert_time = alert.get("alertDate", "N/A")
            city = alert.get("data", "N/A")
            print(Fore.RED + f"Time: {alert_time}, Location: {city}, Type: Active")
    else:
        print("No active rocket alerts.")

    print(Fore.RESET + "\n--- Upcoming Alerts ---")
    if upcoming_alerts:
        for alert in upcoming_alerts:
            alert_time = alert.get("alertDate", "N/A")
            city = alert.get("data", "N/A")
            print(Fore.YELLOW + f"Time: {alert_time}, Location: {city}, Type: Upcoming")
    else:
        print("No upcoming alerts.")

    print(Fore.RESET + "\n--- Aircraft Intrusion Alerts ---")
    if aircraft_intrusion_alerts:
        for alert in aircraft_intrusion_alerts:
            alert_time = alert.get("alertDate", "N/A")
            city = alert.get("data", "N/A")
            title = re.sub(r'\s+', ' ', alert.get("title", "N/A")).strip()
            print(Fore.BLUE + f"Time: {alert_time}, Location: {city}, Type: {title}")
    else:
        print("No aircraft intrusion alerts.")

    print(Fore.RESET + "\n--- Ended Alerts ---")
    if ended_alerts:
        for alert in ended_alerts:
            alert_time = alert.get("alertDate", "N/A")
            city = alert.get("data", "N/A")
            title = re.sub(r'\s+', ' ', alert.get("title", "N/A")).strip()
            print(Fore.LIGHTBLACK_EX + f"Time: {alert_time}, Location: {city}")
            print(Fore.LIGHTBLACK_EX + f"  Type: {title}")
    else:
        print("No ended alerts.")

    if unexpected_alerts:
        print(Fore.RESET + "\n--- Unexpected Alerts ---")
        for alert in unexpected_alerts:
            alert_time = alert.get("alertDate", "N/A")
            city = alert.get("data", "N/A")
            title = re.sub(r'\s+', ' ', alert.get("title", "N/A")).strip()
            print(Fore.MAGENTA + f"Warning: Unexpected alert type: '{title}'")
            print(Fore.MAGENTA + f"  Time: {alert_time}, Location: {city}")

    print(Fore.RESET)

    if log_file:
        log_alerts(log_file, active_alerts, upcoming_alerts, aircraft_intrusion_alerts, ended_alerts, unexpected_alerts)
        print(f"\nResults logged to {log_file}")


def categorize_alerts(alerts):
    """Categorizes alerts into active, upcoming, aircraft intrusion, ended, and unexpected."""
    active_alerts = []
    upcoming_alerts = []
    aircraft_intrusion_alerts = []
    ended_alerts = []
    unexpected_alerts = []

    for alert in alerts:
        title = alert.get("title", "")
        if re.search(r'-\s+האירוע הסתיים', title):
            ended_alerts.append(alert)
        elif title == "ירי רקטות וטילים":
            active_alerts.append(alert)
        elif title == "בדקות הקרובות צפויות להתקבל התרעות באזורך":
            upcoming_alerts.append(alert)
        elif "חדירת כלי טיס עוין" in title:
            aircraft_intrusion_alerts.append(alert)
        else:
            unexpected_alerts.append(alert)

    return active_alerts, upcoming_alerts, aircraft_intrusion_alerts, ended_alerts, unexpected_alerts


def process_alerts(log_file="alerts.log"):
    """Main function to fetch, save, and display alerts."""
    alerts_data = fetch_alerts()
    if alerts_data:
        save_alerts(alerts_data)
        active_alerts, upcoming_alerts, aircraft_intrusion_alerts, ended_alerts, unexpected_alerts = categorize_alerts(alerts_data)
        display_alerts(active_alerts, upcoming_alerts, aircraft_intrusion_alerts, ended_alerts, unexpected_alerts, log_file)
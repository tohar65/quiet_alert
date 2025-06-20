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

def display_alerts(active_alerts, upcoming_alerts):
    """Displays active and upcoming alerts."""
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
    print(Fore.RESET)

def categorize_alerts(alerts):
    """Categorizes alerts into active and upcoming."""
    active_alerts = []
    upcoming_alerts = []
    
    for alert in alerts:
        if alert.get("title") == "ירי רקטות וטילים":
            active_alerts.append(alert)
        else:
            upcoming_alerts.append(alert)
            
    return active_alerts, upcoming_alerts

def process_alerts():
    """Main function to fetch, save, and display alerts."""
    alerts_data = fetch_alerts()
    if alerts_data:
        save_alerts(alerts_data)
        active_alerts, upcoming_alerts = categorize_alerts(alerts_data)
        display_alerts(active_alerts, upcoming_alerts)
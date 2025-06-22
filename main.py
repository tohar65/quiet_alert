import json
import os
import sys
import argparse
from datetime import datetime
from colorama import init
from alert_parser import fetch_alerts, categorize_alerts, display_alerts, save_alerts

def main():
    """
    Main function to fetch, process, and display alerts.
    Supports filtering by location and logging to a file.
    """
    init()

    parser = argparse.ArgumentParser(description='Fetch and display alerts.')
    parser.add_argument('--locations', nargs='*', help='A list of locations to filter alerts by.')
    args = parser.parse_args()

    alerts_data = fetch_alerts()
    if alerts_data:
        if args.locations:
            alerts_data = [
                alert for alert in alerts_data if alert.get('data') in args.locations
            ]

        # Log each raw alert to a file, ensuring UTF-8 encoding with a BOM
        file_exists = os.path.exists('alerts.log')
        with open('alerts.log', 'a', encoding='utf-8') as f:
            if not file_exists or os.path.getsize('alerts.log') == 0:
                f.write('\ufeff')  # UTF-8 BOM
            
            if not alerts_data:
                f.write("--- Active Alerts ---\n")
                f.write("No active alerts.\n")
                f.write("--- Ended Alerts ---\n")
                f.write("No ended alerts.\n")
            else:
                for alert in alerts_data:
                    location = alert.get('data', 'N/A')
                    threat = alert.get('title', 'N/A')
                    category = alert.get('category', 0)

                    if category in [1, 3, 4]:
                        threat_type = "rocket"
                    elif category == 2:
                        threat_type = "aircraft intrusion"
                    else:
                        threat_type = "other"
                    
                    f.write(f"Location: {location}, Threat: {threat}, Threat Type: {threat_type}\n")

        alerts = categorize_alerts(alerts_data)

        save_alerts(alerts)
        display_alerts(alerts)

if __name__ == "__main__":
    main()
import json
import os
from datetime import datetime
from colorama import init
from alert_parser import fetch_alerts, categorize_alerts, display_alerts, save_alerts

def main():
    """
    Main function to fetch, process, and display alerts.
    Supports filtering by location and logging to a file.
    """
    init()

    alerts_data = fetch_alerts()
    if alerts_data:
        # Log each raw alert to a file, ensuring UTF-8 encoding with a BOM
        file_exists = os.path.exists('alerts.log')
        with open('alerts.log', 'ab') as f:
            if not file_exists or os.path.getsize('alerts.log') == 0:
                f.write(b'\xef\xbb\xbf')  # UTF-8 BOM
            for alert in alerts_data:
                f.write(json.dumps(alert, ensure_ascii=False).encode('utf-8') + b'\n')

        alerts = categorize_alerts(alerts_data)

        save_alerts(alerts)
        display_alerts(alerts)

if __name__ == "__main__":
    main()
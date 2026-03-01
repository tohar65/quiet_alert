import json
import os
import sys
import argparse
from datetime import datetime
from colorama import init
from .parser import OrefAlertParser, fetch_alerts, save_alerts, display_alerts, filter_alerts_by_location
from .models import Alert

def main() -> None:
    """
    Main function to fetch, process, and display alerts.

    Supports filtering by location and logging to a file.
    Can also be used to launch the web server.

    Returns:
        None
    """
    init()

    arg_parser = argparse.ArgumentParser(description='Fetch and display alerts.')
    arg_parser.add_argument('--locations', nargs='*', help='A list of locations to filter alerts by.')
    arg_parser.add_argument('--web', action='store_true', help='Run the web server.')
    args = arg_parser.parse_args()

    if args.web:
        from web_app.web_server import app
        app.run(debug=True)
        return

    alerts_data = fetch_alerts()
    if alerts_data:
        parser = OrefAlertParser(alerts_data)
        alerts = parser.get_alerts()

        if args.locations:
            alerts = filter_alerts_by_location(alerts, args.locations)

        # Log each filtered alert as a JSON string to a file
        with open('alerts.log', 'a', encoding='utf-8') as f:
            for alert in alerts:
                f.write(json.dumps(alert.to_dict(), ensure_ascii=False) + '\n')

        save_alerts(alerts)
        display_alerts(alerts)

if __name__ == "__main__":
    main()
import argparse
from colorama import init
from alert_parser import fetch_alerts, categorize_alerts, filter_alerts_by_location, display_alerts, save_alerts

def main():
    """
    Main function to fetch, process, and display alerts.
    Supports filtering by location.
    """
    init() 

    parser = argparse.ArgumentParser(description="Fetch and display alerts from Pikud Haoref.")
    parser.add_argument(
        '--locations', 
        nargs='*', 
        help='A list of locations to filter alerts by (e.g., "New York" "Los Angeles").'
    )
    parser.add_argument(
        '--log-file', 
        default='alerts.log', 
        help='The file to log alerts to.'
    )
    args = parser.parse_args()

    alerts_data = fetch_alerts()
    if alerts_data:
        alerts = categorize_alerts(alerts_data)
        
        if args.locations:
            alerts = filter_alerts_by_location(alerts, args.locations)
        
        save_alerts(alerts)
        display_alerts(alerts, log_file=args.log_file)

if __name__ == "__main__":
    main()
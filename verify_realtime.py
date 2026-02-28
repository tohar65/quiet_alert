import sys
import os

# Ensure the package is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'oref_alert_parser')))

from oref_alert_parser.parser import fetch_realtime_alerts, OrefAlertParser

def main():
    print("Fetching real-time alerts...")
    try:
        raw_alerts = fetch_realtime_alerts()
        print(f"Raw alerts fetched: {raw_alerts}")
        
        if raw_alerts:
            parser = OrefAlertParser(raw_alerts)
            alerts = parser.get_alerts()
            print(f"Parsed {len(alerts)} alerts:")
            for alert in alerts:
                print(f"- {alert.title} in {alert.location} at {alert.alertDate} ({alert.status})")
        else:
            print("No active alerts at the moment.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

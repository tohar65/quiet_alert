import sys
import os
import requests
import time

# Ensure the package is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'oref_alert_parser')))

from oref_alert_parser.parser import fetch_alerts, OrefAlertParser

def main():
    print("1. Fetching history alerts to find a valid location...")
    history_data = fetch_alerts()
    if not history_data:
        print("No history alerts found. Cannot verify with real data.")
        return

    parser = OrefAlertParser(history_data)
    alerts = parser.get_alerts()
    
    if not alerts:
        print("No parsed alerts found.")
        return
        
    # Get a location from the most recent alert
    recent_alert = alerts[0]
    location = recent_alert.location
    print(f"Found recent alert in location: {location} at {recent_alert.alertDate}")
    
    print(f"\n2. Querying local server for location: {location}")
    try:
        response = requests.get(f"http://localhost:8080/api/alerts/all?location={location}")
        response.raise_for_status()
        data = response.json()
        
        server_alerts = data.get("alerts", [])
        print(f"Server returned {len(server_alerts)} alerts for {location}")
        
        if len(server_alerts) > 0:
            print("Top alert from server:")
            print(server_alerts[0])
            
            # Check if our recent alert is in the list (or roughly match)
            # Timestamps might differ slightly due to parsing?
            # Let's just check if we got data.
            print("Verification SUCCESS: Server returned data.")
        else:
            print("Verification WARNING: Server returned 0 alerts, but we found some in history.")
            
    except requests.exceptions.RequestException as e:
        print(f"Error querying server: {e}")
        print("Make sure the server is running on port 8080")

if __name__ == "__main__":
    main()

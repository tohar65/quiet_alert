import requests
import json
import urllib.parse
import sys
import os
from datetime import datetime

# Add parent directory to path to import oref_alert_parser
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from oref_alert_parser.oref_alert_parser.oref_provider import OrefProvider
from web_app.config import config

def diagnose():
    city = "פתח תקווה"
    encoded_city = urllib.parse.quote(city)
    
    # 1. Direct API call (Specific to city as requested by user)
    specific_url = f"https://alerts-history.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&mode=1&city_0={encoded_city}"
    headers = {
        'User-Agent': config.USER_AGENT,
        'Referer': 'https://www.oref.org.il/heb/alerts-history'
    }
    
    print(f"--- Step 1: Fetching directly from API for {city} ---")
    try:
        resp = requests.get(specific_url, headers=headers)
        resp.raise_for_status()
        # Handle BOM
        content = resp.content.decode('utf-8-sig')
        direct_data = json.loads(content)
        print(f"Direct API returned {len(direct_data)} alerts for {city}.")
        if direct_data:
            print(f"Latest direct alert date: {direct_data[0].get('alertDate')}")
    except Exception as e:
        print(f"Error in Step 1: {e}")
        direct_data = []

    # 2. Provider Fetch (General history as used in the app)
    print(f"\n--- Step 2: Fetching using OrefProvider (General History) ---")
    provider = OrefProvider(
        history_url=config.OREF_HISTORY_URL,
        realtime_url=config.OREF_REALTIME_URL,
        user_agent=config.USER_AGENT
    )
    
    provider_alerts = provider.fetch_history_alerts()
    print(f"OrefProvider returned {len(provider_alerts)} total alerts.")
    
    # Filter for the city
    provider_city_alerts = [a for a in provider_alerts if (isinstance(a.location, list) and city in a.location) or a.location == city]
    print(f"OrefProvider has {len(provider_city_alerts)} alerts for {city}.")
    if provider_city_alerts:
        print(f"Latest provider alert date: {provider_city_alerts[0].alertDate}")

    # 3. Backend Logic Simulation (Deduplication and Filtering)
    print(f"\n--- Step 3: Simulating Backend Processing (web_server.py) ---")
    # Simulation of all_alerts() route logic
    location = city
    all_alerts_list = provider_alerts # Simulation: only history for now
    
    location_alerts = []
    for alert in all_alerts_list:
        if isinstance(alert.location, list):
            if location in alert.location:
                location_alerts.append(alert)
        elif alert.location == location:
            location_alerts.append(alert)
            
    unique_alerts = {}
    for alert in location_alerts:
        if alert.id:
            key = (alert.id, location)
        else:
            date_key = str(alert.alertDate)[:16] if alert.alertDate else None
            key = (date_key, location, alert.threat_type)
        
        if key not in unique_alerts:
            unique_alerts[key] = alert

    final_alerts = sorted(unique_alerts.values(), key=lambda x: x.alertDate if x.alertDate else datetime.min, reverse=True)
    backend_count = len(final_alerts)
    print(f"Backend simulation returned {backend_count} unique alerts for {city}.")

    # 4. Frontend Logic Simulation (Deduplication and Limits)
    print(f"\n--- Step 4: Simulating Frontend Processing (app.js) ---")
    # Simulation of displayHistory limit and deduplicateAlerts
    # In app.js: const alertsToShow = deduplicatedAlerts.slice(1, historyLimit + 1); 
    # default historyLimit is 10
    history_limit = 10
    
    # deduplicateAlerts in JS is slightly different but similar to backend
    # Just checking the slice:
    frontend_visible = final_alerts[1:history_limit+1]
    print(f"Frontend would show {len(frontend_visible)} alerts in the history section (Limit: {history_limit}).")
    print(f"Total available in frontend data: {len(final_alerts[:100])}")

    # 5. Conclusion
    print("\n--- Summary ---")
    print(f"API (Specific to city): {len(direct_data)}")
    print(f"API (General History used by app): {len(provider_alerts)} total, {len(provider_city_alerts)} for {city}")
    print(f"Backend Unique: {backend_count}")
    print(f"Frontend Displayed in History section: {len(frontend_visible)}")

if __name__ == "__main__":
    diagnose()

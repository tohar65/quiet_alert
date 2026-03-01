import os
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from oref_alert_parser.parser import OrefAlertParser, fetch_realtime_alerts, fetch_alerts
from oref_alert_parser.approved_locations import APPROVED_LOCATIONS

app = Flask(__name__, static_folder='static', template_folder='templates')

# In-memory cache for real-time alerts and history
realtime_alerts_cache = []
history_cache = []
last_history_fetch = 0
cache_lock = threading.Lock()

def poll_realtime_alerts():
    """Background thread function to continuously poll for real-time alerts and history."""
    global realtime_alerts_cache, history_cache, last_history_fetch
    while True:
        try:
            # Poll Realtime
            alerts_data = fetch_realtime_alerts()
            if alerts_data:
                parser = OrefAlertParser(alerts_data)
                parsed_alerts = parser.get_alerts()
                
                with cache_lock:
                    # Merge new alerts with existing cache, avoiding duplicates
                    existing_keys = {
                        (a.alertDate, tuple(a.location) if isinstance(a.location, list) else a.location, a.threat_type) 
                        for a in realtime_alerts_cache
                    }
                    
                    for alert in parsed_alerts:
                        loc_key = tuple(alert.location) if isinstance(alert.location, list) else alert.location
                        key = (alert.alertDate, loc_key, alert.threat_type)
                        if key not in existing_keys:
                            realtime_alerts_cache.append(alert)
                            existing_keys.add(key)
                    
                    if len(realtime_alerts_cache) > 1000:
                        from datetime import datetime as dt, timezone
                        realtime_alerts_cache.sort(key=lambda a: a.alertDate if a.alertDate else dt.min.replace(tzinfo=timezone.utc), reverse=True)
                        realtime_alerts_cache = realtime_alerts_cache[:1000]

            # Poll History every 10 seconds or if never fetched
            if time.time() - last_history_fetch > 10:
                history_data = fetch_alerts()
                if history_data:
                    history_parser = OrefAlertParser(history_data)
                    new_history = history_parser.get_alerts()
                    with cache_lock:
                        history_cache = new_history
                    last_history_fetch = time.time()

        except Exception as e:
            print(f"Error polling alerts: {e}")
            
        time.sleep(2)

# Start background polling thread
polling_thread = threading.Thread(target=poll_realtime_alerts, daemon=True)
polling_thread.start()


@app.route('/')
def index():
    """
    Serves the main page.
    """
    return render_template('index.html')


@app.route('/alerts')
def alerts():
    """
    Provides the alert data as a JSON object.
    """
    with cache_lock:
        return jsonify([alert.to_dict() for alert in realtime_alerts_cache])


@app.route('/api/approved-locations')
def approved_locations():
    """
    Returns the list of approved locations.
    """
    return jsonify({'locations': APPROVED_LOCATIONS})


@app.route('/api/force-refresh', methods=['POST'])
def force_refresh():
    """
    Forces the backend to prepare for a fresh history fetch.
    Does NOT clear the cache to avoid UI flickers.
    """
    global last_history_fetch
    with cache_lock:
        last_history_fetch = 0 # Force re-fetch on next poll cycle
    return jsonify({"status": "success"})


@app.route('/api/alerts/all')
def all_alerts():
    """
    Provides all historical alerts for a specific location.
    """
    location = request.args.get('location')
    if not location:
        return jsonify({"error": "Location parameter is required"}), 400
    
    # Use cached alerts for speed
    with cache_lock:
        realtime_alerts = list(realtime_alerts_cache)
        history_alerts = list(history_cache)

    # Combine all alerts
    all_alerts_list = realtime_alerts + history_alerts

    # Filter by location
    location_alerts = []
    for alert in all_alerts_list:
        if isinstance(alert.location, list):
            if location in alert.location:
                location_alerts.append(alert)
        elif alert.location == location:
            location_alerts.append(alert)

    # Deduplicate based on ID or (date, location, threat)
    # Since Alert object doesn't have ID, we use a unique key.
    # We want to keep the most recent one if duplicates exist (though they should be identical usually)
    unique_alerts = {}
    for alert in location_alerts:
        # Key: (date up to minute to handle slight variations, location, threat_type)
        # Handle datetime formats
        date_key = str(alert.alertDate)[:16] if alert.alertDate else None
        
        # We need to flatten location for the key if it's a list and we matched one item
        # But wait, if we are filtering by a single location string, the alert.location could be a list
        # For deduplication, if the same alert from realtime vs history has list vs string, they might mismatch
        # But the frontend expects `alert.location` to be something it can display.
        # Let's just use the `location` query param as the key part since we already filtered by it.
        key = (date_key, location, alert.threat_type)
        
        if key not in unique_alerts:
            # Create a copy or modify the alert to ensure location is a string for the frontend
            # The frontend expects location to be a string.
            if isinstance(alert.location, list):
                import copy
                alert_copy = copy.copy(alert)
                alert_copy.location = location
                unique_alerts[key] = alert_copy
            else:
                unique_alerts[key] = alert
    
    # Sort by date descending
    # Use datetime.min for alerts with no date so they appear last (or first if ascending, but we want reverse)
    # Since alertDate is naive datetime (as per parser), we can use datetime.min
    from datetime import datetime
    final_alerts = sorted(unique_alerts.values(), key=lambda x: x.alertDate if x.alertDate else datetime.min, reverse=True)

    # Return top 50
    return jsonify({
        "alerts": [alert.to_dict() for alert in final_alerts[:50]],
        "syncing": last_history_fetch == 0
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
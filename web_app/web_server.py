import os
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from typing import List, Dict, Any, Tuple, Optional
from oref_alert_parser.parser import OrefAlertParser
from oref_alert_parser.approved_locations import APPROVED_LOCATIONS
from oref_alert_parser.models import Alert
from oref_alert_parser.provider import AlertProvider
from oref_alert_parser.oref_provider import OrefProvider
from web_app.config import config

app = Flask(__name__, static_folder='static', template_folder='templates')

# In-memory cache for real-time alerts and history
realtime_alerts_cache: List[Alert] = []
history_cache: List[Alert] = []
last_history_fetch: float = 0
cache_lock = threading.Lock()

# Alert provider instance (dependency injection)
alert_provider: Optional[AlertProvider] = None

def get_provider() -> AlertProvider:
    """
    Returns the configured alert provider.
    Initializes OrefProvider if no provider is set.
    """
    global alert_provider
    if alert_provider is None:
        alert_provider = OrefProvider(
            history_url=config.OREF_HISTORY_URL,
            realtime_url=config.OREF_REALTIME_URL,
            user_agent=config.USER_AGENT
        )
    return alert_provider

def poll_realtime_alerts() -> None:
    """
    Background thread function to continuously poll for real-time alerts and history.
    Updates the in-memory caches and ensures they don't grow indefinitely.
    """
    global realtime_alerts_cache, history_cache, last_history_fetch
    provider = get_provider()
    
    while True:
        try:
            # Poll Realtime
            parsed_alerts = provider.fetch_realtime_alerts()
            if parsed_alerts:
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
                        del realtime_alerts_cache[1000:]

            # Poll History based on configured interval or if never fetched
            if time.time() - last_history_fetch > config.POLL_INTERVAL_HISTORY:
                new_history = provider.fetch_history_alerts()
                if new_history:
                    with cache_lock:
                        history_cache[:] = new_history
                    last_history_fetch = time.time()

        except Exception as e:
            print(f"Error polling alerts: {e}")
            
        time.sleep(config.POLL_INTERVAL_REALTIME)


@app.route('/')
def index() -> str:
    """
    Serves the main page.
    """
    return render_template('index.html')


@app.route('/alerts')
def alerts() -> Any:
    """
    Provides the alert data as a JSON object.
    """
    with cache_lock:
        return jsonify([alert.to_dict() for alert in realtime_alerts_cache])


@app.route('/api/approved-locations')
def approved_locations() -> Any:
    """
    Returns the list of approved locations.
    """
    return jsonify({'locations': APPROVED_LOCATIONS})


@app.route('/api/force-refresh', methods=['POST'])
def force_refresh() -> Any:
    """
    Forces the backend to prepare for a fresh history fetch.
    """
    global last_history_fetch
    with cache_lock:
        last_history_fetch = 0 # Force re-fetch on next poll cycle
    return jsonify({"status": "success"})


@app.route('/api/alerts/all')
def all_alerts() -> Any:
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

    # Deduplicate
    unique_alerts = {}
    for alert in location_alerts:
        date_key = str(alert.alertDate)[:16] if alert.alertDate else None
        key = (date_key, location, alert.threat_type)
        
        if key not in unique_alerts:
            if isinstance(alert.location, list):
                import copy
                alert_copy = copy.copy(alert)
                alert_copy.location = location
                unique_alerts[key] = alert_copy
            else:
                unique_alerts[key] = alert
    
    # Sort by date descending
    from datetime import datetime as dt
    final_alerts = sorted(unique_alerts.values(), key=lambda x: x.alertDate if x.alertDate else dt.min, reverse=True)

    # Return top 50
    return jsonify({
        "alerts": [alert.to_dict() for alert in final_alerts[:50]],
        "syncing": last_history_fetch == 0
    })


def run_server(provider: Optional[AlertProvider] = None) -> None:
    """
    Starts the web server and background polling.
    Allows injecting a custom provider.
    """
    global alert_provider
    if provider:
        alert_provider = provider

    # Start background polling thread
    polling_thread = threading.Thread(target=poll_realtime_alerts, daemon=True)
    polling_thread.start()

    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=config.DEBUG)


if __name__ == '__main__':
    run_server()

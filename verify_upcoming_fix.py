
import sys
import os
import json
from datetime import datetime, timedelta

# Add the project root to sys.path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'oref_alert_parser'))

from oref_alert_parser.parser import OrefAlertParser
from oref_alert_parser.models import AlertStatus

def test_upcoming_merging_and_colors():
    # Scenario: Two "Upcoming" pulses for the same event at 13:22 and 13:23
    # Pulse 1: 13:22, Category 14
    # Pulse 2: 13:23, Category 14
    
    base_time = datetime(2026, 3, 1, 13, 22, 0)
    
    raw_data = [
        {
            "alertDate": base_time.strftime("%Y-%m-%d %H:%M:%S"),
            "title": "In the coming minutes, alerts are expected in your area",
            "data": ["פתח תקווה"],
            "category": 14,
            "category_desc": "In the coming minutes, alerts are expected in your area",
            "id": "1234567890"
        },
        {
            "alertDate": (base_time + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "title": "In the coming minutes, alerts are expected in your area",
            "data": ["פתח תקווה"],
            "category": 14,
            "category_desc": "In the coming minutes, alerts are expected in your area",
            "id": "1234567891"
        }
    ]
    
    parser = OrefAlertParser(raw_data)
    alerts = parser.get_alerts()
    
    print(f"Parsed {len(alerts)} alerts")
    for a in alerts:
        print(f"Alert: {a.alertDate}, Status: {a.status}, Category: {a.oref_category}, ID: {a.id}")
        assert a.status == AlertStatus.UPCOMING
        assert a.oref_category == 14

    # Backend deduplication (OrefAlertParser._deduplicate_alerts) currently uses:
    # str(alert.alertDate)[:16]  # e.g., up to minute
    # So 13:22 and 13:23 will NOT be merged by the backend if they have different minutes and IDs.
    # This is intended as the backend should keep the history.
    # The frontend is responsible for the "Display Merge".
    
    # Let's verify our frontend logic via a simulated call
    # In app.js:
    # timeDiff <= 300000 (5 mins) for upcoming
    
    def simulate_frontend_deduplicate(alerts):
        deduplicated = []
        for alert in alerts:
            is_duplicate = False
            for existing in deduplicated:
                # Content match
                content_match = (existing.title == alert.title and existing.message == alert.message)
                same_location = existing.location == alert.location
                
                # Time diff
                alert_time = datetime.fromisoformat(alert.alertDate) if isinstance(alert.alertDate, str) else alert.alertDate
                existing_time = datetime.fromisoformat(existing.alertDate) if isinstance(existing.alertDate, str) else existing.alertDate
                time_diff_ms = abs((existing_time - alert_time).total_seconds() * 1000)
                
                is_upcoming = alert.status == "upcoming" or existing.status == "upcoming" or \
                             alert.oref_category == 14 or existing.oref_category == 14
                
                if is_upcoming and same_location and content_match and time_diff_ms <= 300000:
                    is_duplicate = True
                    break
            if not is_duplicate:
                deduplicated.push(alert) if hasattr(deduplicated, 'push') else deduplicated.append(alert)
        return deduplicated

    display_alerts = simulate_frontend_deduplicate(alerts)
    print(f"Frontend simulated merge: {len(display_alerts)} alert(s) displayed")
    assert len(display_alerts) == 1
    
    # Test color logic simulation
    def get_color(alert):
        if "ניתן לצאת מהמרחב המוגן" in alert.title: return "green"
        if alert.status == AlertStatus.UPCOMING or alert.oref_category == 14: return "yellow"
        return "red"
        
    print(f"Color for pulse 1: {get_color(alerts[0])}")
    print(f"Color for pulse 2: {get_color(alerts[1])}")
    assert get_color(alerts[0]) == "yellow"
    assert get_color(alerts[1]) == "yellow"

if __name__ == "__main__":
    test_upcoming_merging_and_colors()
    print("Test passed!")

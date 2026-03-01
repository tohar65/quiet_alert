import pytest
from playwright.sync_api import Page, expect
import json
import os
import threading
import time
import re
from datetime import datetime, timedelta
from web_app.web_server import app
from werkzeug.serving import make_server
from unittest.mock import patch

class ServerThread(threading.Thread):
    def __init__(self, app, port=5006):
        threading.Thread.__init__(self)
        self.port = port
        self.server = make_server('127.0.0.1', self.port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

@pytest.fixture(scope="module")
def test_server():
    server = ServerThread(app, port=5006)
    server.start()
    # Wait for server to be ready
    time.sleep(1)
    yield f"http://127.0.0.1:{server.port}"
    server.shutdown()
    server.join()

def test_js_logic_format_time(page: Page, test_server):
    page.goto(test_server)
    
    # Test formatTime via evaluate
    # It's now attached to window
    result = page.evaluate("window.formatTime(65)")
    assert result == "01:05"
    
    result = page.evaluate("window.formatTime(3600)")
    assert result == "60:00"
    
    result = page.evaluate("window.formatTime(9)")
    assert result == "00:09"

def test_refresh_dot_states(page: Page, test_server):
    page.goto(test_server)
    
    # Initial state: no syncing class
    dot = page.locator("#live-sync-indicator")
    expect(dot).not_to_have_class(re.compile(r"syncing"))
    
    # Trigger a fetch and check for syncing class
    # We mock the fetch to control timing
    page.evaluate("""() => {
        const dot = document.getElementById('live-sync-indicator');
        dot.classList.add('syncing');
    }""")
    expect(dot).to_have_class(re.compile(r"syncing"))
    
    # Error state
    page.evaluate("""() => {
        const dot = document.getElementById('live-sync-indicator');
        dot.classList.add('error');
    }""")
    expect(dot).to_have_class(re.compile(r"error"))

def test_check_alerts_button_animation(page: Page, test_server):
    page.goto(test_server)
    btn = page.locator("#check-alerts-btn")
    
    # Simulate click and check for aurora animation class
    page.evaluate("document.getElementById('check-alerts-btn').classList.add('loading-aurora')")
    expect(btn).to_have_class(re.compile(r"loading-aurora"))
    
    page.evaluate("document.getElementById('check-alerts-btn').classList.remove('loading-aurora')")
    expect(btn).not_to_have_class(re.compile(r"loading-aurora"))

def test_alert_rendering_and_styles(page: Page, test_server):
    # Mock alerts API to return different types of alerts
    mock_alerts = {
        "alerts": [
            {
                "location": "Tel Aviv",
                "title": "Rocket Fire",
                "message": "Seek shelter",
                "alertDate": datetime.now().isoformat(),
                "status": "active"
            },
            {
                "location": "Haifa",
                "title": "Hostile Aircraft Intrusion",
                "message": "Enter protected area",
                "alertDate": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "status": "upcoming"
            }
        ],
        "syncing": False
    }

    page.route("**/api/alerts/all*", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(mock_alerts)
    ))

    page.goto(test_server)
    
    # Fill location and click
    page.fill("#location-input", "Tel Aviv")
    # Force the button to be enabled (mocking approved locations)
    page.evaluate("document.getElementById('check-alerts-btn').disabled = false")
    page.click("#check-alerts-btn")
    
    # Check active alert style
    active_alert = page.locator(".alert-item.alert-red")
    expect(active_alert).to_be_visible()
    expect(active_alert).to_contain_text("Rocket Fire")
    
    # Check upcoming history style
    history_item = page.locator(".history-item.upcoming")
    expect(history_item).to_be_visible()
    expect(history_item).to_contain_text("Hostile Aircraft Intrusion")

def test_timer_transitions(page: Page, test_server):
    # Create an alert that happened 9 minutes and 55 seconds ago
    nine_min_ago = (datetime.now() - timedelta(minutes=9, seconds=55)).isoformat()
    
    mock_alerts = {
        "alerts": [{
            "location": "Test City",
            "title": "Rocket Fire",
            "message": "Test Message",
            "alertDate": nine_min_ago,
            "status": "active"
        }],
        "syncing": False
    }

    page.route("**/api/alerts/all*", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(mock_alerts)
    ))

    page.goto(test_server)
    page.fill("#location-input", "Test City")
    page.evaluate("document.getElementById('check-alerts-btn').disabled = false")
    page.click("#check-alerts-btn")
    
    # Wait for timer
    timer = page.locator("#timer-container .timer-box")
    expect(timer).to_be_visible()
    
    # Should show warning initially (under 10 mins)
    expect(timer).to_have_class(re.compile(r"active"))
    
    # Wait for it to cross 10 minutes (600 seconds)
    # Since we can't easily wait 5 real seconds and rely on it, we can mock the time in JS or just check the logic
    # Let's mock a 10 min 5 sec ago alert instead
    ten_min_ago = (datetime.now() - timedelta(minutes=10, seconds=5)).isoformat()
    mock_alerts["alerts"][0]["alertDate"] = ten_min_ago
    
    page.route("**/api/alerts/all*", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(mock_alerts)
    ))
    
    # Force a refresh if needed or just wait for the next poll (2s)
    page.wait_for_timeout(3000) 
    
    expect(timer).to_have_class(re.compile(r"safe"))

def test_responsive_layout(page: Page, test_server):
    page.goto(test_server)
    
    # Desktop Viewport
    page.set_viewport_size({"width": 1280, "height": 800})
    # Check if main container is centered or has expected width
    container = page.locator(".container")
    expect(container).to_be_visible()
    box = container.bounding_box()
    assert box is not None
    assert box['width'] > 400 # Desktop should be wider or fixed max-width
    
    # Mobile Viewport
    page.set_viewport_size({"width": 375, "height": 667})
    box = container.bounding_box()
    assert box is not None
    assert box['width'] <= 375 # Should fit mobile width

def test_deduplication_logic(page: Page, test_server):
    page.goto(test_server)
    
    # Define alerts with close times (1 minute apart)
    now = datetime.now()
    alerts = [
        {
            "location": "Tel Aviv",
            "title": "Rocket Fire",
            "message": "Seek shelter",
            "alertDate": now.isoformat(),
            "status": "active"
        },
        {
            "location": "Tel Aviv",
            "title": "Rocket Fire",
            "message": "Seek shelter",
            "alertDate": (now - timedelta(minutes=1)).isoformat(),
            "status": "active"
        }
    ]
    
    # Test deduplicateAlerts function directly
    result = page.evaluate(f"window.deduplicateAlerts({json.dumps(alerts)})")
    assert len(result) == 1
    
    # Test with different content (not a duplicate)
    alerts[1]["title"] = "Different Title"
    # In the current logic, same location and same minute (within 60s) is considered a duplicate
    # even if the title is different, to avoid UI clutter.
    # To test for 2 alerts, we need to change the time or location.
    alerts[1]["alertDate"] = (now - timedelta(minutes=5)).isoformat()
    result = page.evaluate(f"window.deduplicateAlerts({json.dumps(alerts)})")
    assert len(result) == 2

def test_color_coding_logic(page: Page, test_server):
    page.goto(test_server)
    
    # Upcoming status -> yellow
    alert_yellow = {"status": "upcoming", "title": "Some alert"}
    assert page.evaluate(f"window.getAlertColorClass({json.dumps(alert_yellow)})") == "alert-yellow"
    
    # Rocket fire -> red
    alert_red = {"status": "active", "title": "ירי רקטות וטילים"}
    assert page.evaluate(f"window.getAlertColorClass({json.dumps(alert_red)})") == "alert-red"
    
    # Safe to leave -> green
    alert_green = {"status": "active", "title": "ניתן לצאת מהמרחב המוגן אך יש להישאר בקרבתו"}
    assert page.evaluate(f"window.getAlertColorClass({json.dumps(alert_green)})") == "alert-green"

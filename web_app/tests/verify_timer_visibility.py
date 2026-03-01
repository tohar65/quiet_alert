import pytest
from playwright.sync_api import Page, expect
import json
import os
import threading
from web_app.web_server import app
from werkzeug.serving import make_server
from unittest.mock import patch

# Use the same test data structure
TEST_DATA = {
    "alerts": [
        {
            "id": "1",
            "title": "ניתן לצאת מהמרחב המוגן אך יש להישאר בקרבתו",
            "location": "פתח תקווה",
            "alertDate": "2026-02-28T17:35:41",
            "category": "instruction",
            "status": "ended"
        }
    ]
}

RAW_OREF_DATA = [{
    "data": alert["location"],
    "category": alert["category"],
    "alertDate": alert["alertDate"].replace("T", " "),
    "title": alert["title"],
    "id": alert["id"]
} for alert in TEST_DATA["alerts"]]

class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 5006, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

@pytest.fixture(scope="module")
def test_server():
    with patch("web_app.web_server.fetch_alerts", return_value=RAW_OREF_DATA), \
         patch("web_app.web_server.fetch_realtime_alerts", return_value=[]):
        server = ServerThread(app)
        server.start()
        yield
        server.shutdown()
        server.join()

def test_timer_hidden_for_safe_to_leave(page: Page, test_server):
    def handle_locations(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"locations": ["פתח תקווה"]})
        )

    page.route("**/api/approved-locations*", handle_locations)
    page.goto("http://127.0.0.1:5006/")
    
    page.fill("#location-input", "פתח תקווה")
    page.click("#check-alerts-btn")

    # Wait for alerts to load
    page.wait_for_selector(".alert-item")
    
    # Check alert message is present
    expect(page.locator("text='ניתן לצאת מהמרחב המוגן אך יש להישאר בקרבתו'").first).to_be_visible()
    
    # Check timer is hidden
    timer = page.locator("#timer-container")
    expect(timer).to_be_hidden()

def test_timer_visible_for_regular_alert(page: Page, test_server):
    # Log console messages
    page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))

    # Override the mock for this specific test to show a regular alert
    regular_alert = [{
        "data": "פתח תקווה",
        "category": "missiles",
        "alertDate": "2026-02-28 17:25:34",
        "title": "ירי רקטות וטילים",
        "id": "2"
    }]
    
    with patch("web_app.web_server.fetch_alerts", return_value=regular_alert):
        def handle_locations(route):
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"locations": ["פתח תקווה"]})
            )

        page.route("**/api/approved-locations*", handle_locations)
        page.goto("http://127.0.0.1:5006/")
        
        page.fill("#location-input", "פתח תקווה")
        page.click("#check-alerts-btn")

        # Wait for alerts to load
        page.wait_for_selector(".alert-item")
        
        # Check alert message is present
        expect(page.locator("text='ירי רקטות וטילים'").first).to_be_visible()
        
        # Check timer is visible
        timer = page.locator("#timer-container")
        expect(timer).to_be_visible()

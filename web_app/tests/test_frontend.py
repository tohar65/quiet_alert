import pytest
from playwright.sync_api import Page, expect
import json
import os
import threading
from web_app.web_server import app, get_provider
from werkzeug.serving import make_server
from unittest.mock import patch
import web_app.web_server as ws
from oref_alert_parser.parser import OrefAlertParser

# Central place for test dates and alerts, matching the screenshot exactly
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "test_data.json")
with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
    TEST_DATA = json.load(f)

# Convert TEST_DATA to the raw Oref format so the backend parses it
RAW_OREF_DATA = []
for i, alert in enumerate(TEST_DATA["alerts"]):
    RAW_OREF_DATA.append({
        "data": alert["location"],
        "category": alert["category"],
        # Provide the time in Oref's format without 'T'
        "alertDate": alert["alertDate"].replace("T", " "),
        "title": alert["title"],
        "id": alert["id"]
    })

class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 5005, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

@pytest.fixture(scope="module")
def test_server():
    provider = get_provider()
    # Mock the backend provider methods
    with patch.object(provider, "fetch_history_alerts", return_value=OrefAlertParser(RAW_OREF_DATA).get_alerts()), \
         patch.object(provider, "fetch_realtime_alerts", return_value=[]):
        
        # Manually populate the cache since the background thread is not running
        ws.history_cache = provider.fetch_history_alerts()
        ws.last_history_fetch = 1 # Mark as fetched
        
        server = ServerThread(app)
        server.start()
        yield
        server.shutdown()
        server.join()

def test_frontend_renders_alerts_correctly(page: Page, test_server):
    def handle_locations(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"locations": ["פתח תקווה"]})
        )

    page.route("**/api/approved-locations*", handle_locations)

    page.goto("http://127.0.0.1:5005/")
    
    # Simulate user entering location
    page.fill("#location-input", "פתח תקווה")
    page.click("#check-alerts-btn")

    # Wait for alerts to load
    page.wait_for_selector(".alert-item")

    # Check that the specific texts from the screenshot are present
    expect(page.locator("text='ניתן לצאת מהמרחב המוגן אך יש להישאר בקרבתו'").first).to_be_visible()
    expect(page.locator("text='ירי רקטות וטילים'").first).to_be_visible()
    
    # Check that the exact formatted time matches the screenshot format exactly
    # e.g., "17:35", not "2/28/2026, 7:35:00 PM"
    time_locators = page.locator(".alert-time, .history-time")
    expect(time_locators.nth(0)).to_have_text("17:35")
    expect(time_locators.nth(1)).to_have_text("17:25")
    expect(time_locators.nth(2)).to_have_text("17:18")

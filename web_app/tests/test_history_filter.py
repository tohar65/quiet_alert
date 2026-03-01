import pytest
from playwright.sync_api import Page, expect
import json
from datetime import datetime, timedelta
import threading
import time
from web_app.web_server import app
from werkzeug.serving import make_server

class ServerThread(threading.Thread):
    def __init__(self, app, port=5007):
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
    server = ServerThread(app, port=5007)
    server.start()
    time.sleep(1)
    yield f"http://127.0.0.1:{server.port}"
    server.shutdown()
    server.join()

def test_today_only_filter(page: Page, test_server):
    # Setup: 1 alert from today, 1 alert from yesterday
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    mock_alerts = {
        "alerts": [
            {
                "location": "Tel Aviv",
                "title": "Today's Alert",
                "message": "Today",
                "alertDate": now.isoformat(),
                "status": "active"
            },
            {
                "location": "Tel Aviv",
                "title": "Yesterday's Alert",
                "message": "Yesterday",
                "alertDate": yesterday.isoformat(),
                "status": "active"
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
    
    # Mock approved locations and fill input
    page.evaluate("window.approvedLocations = ['Tel Aviv']")
    page.fill("#location-input", "Tel Aviv")
    page.evaluate("document.getElementById('check-alerts-btn').disabled = false")
    page.click("#check-alerts-btn")
    
    # Check that only "Today's Alert" is visible in the main alert container
    expect(page.locator("#alerts-container")).to_contain_text("Today's Alert")
    expect(page.locator("#alerts-container")).not_to_contain_text("Yesterday's Alert")
    
    # Check history container
    # Since there's only 1 today alert, it becomes the main alert.
    # displayHistory(alertsToShow) will have alertsToShow = deduplicatedAlerts.slice(1) which is empty.
    # So history should say "No past history for today."
    expect(page.locator("#history-container")).to_contain_text("No past history for today.")
    expect(page.locator("#history-container")).not_to_contain_text("Yesterday's Alert")

def test_history_filtering_multiple_today(page: Page, test_server):
    now = datetime.now()
    today_earlier = now - timedelta(hours=2)
    yesterday = now - timedelta(days=1)
    
    mock_alerts = {
        "alerts": [
            {
                "location": "Tel Aviv",
                "title": "Latest Today",
                "message": "Today 1",
                "alertDate": now.isoformat(),
                "status": "active"
            },
            {
                "location": "Tel Aviv",
                "title": "Earlier Today",
                "message": "Today 2",
                "alertDate": today_earlier.isoformat(),
                "status": "active"
            },
            {
                "location": "Tel Aviv",
                "title": "Yesterday's Alert",
                "message": "Yesterday",
                "alertDate": yesterday.isoformat(),
                "status": "active"
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
    page.fill("#location-input", "Tel Aviv")
    page.evaluate("document.getElementById('check-alerts-btn').disabled = false")
    page.click("#check-alerts-btn")
    
    # Main alert: Latest Today
    expect(page.locator("#alerts-container")).to_contain_text("Latest Today")
    
    # History: Earlier Today
    expect(page.locator("#history-container")).to_contain_text("Earlier Today")
    
    # Yesterday's Alert should be nowhere
    expect(page.locator("body")).not_to_contain_text("Yesterday's Alert")

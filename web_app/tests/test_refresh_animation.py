import pytest
import threading
import json
import time
from playwright.sync_api import Page, expect
from web_app.web_server import app, get_provider
from werkzeug.serving import make_server
from unittest.mock import patch
import web_app.web_server as ws

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
    provider = get_provider()
    # Mocking necessary backend functions
    with patch.object(provider, "fetch_history_alerts", return_value=[]), \
         patch.object(provider, "fetch_realtime_alerts", return_value=[]):
        server = ServerThread(app)
        server.start()
        yield
        server.shutdown()
        server.join()

import re

def test_refresh_button_animation(page: Page, test_server):
    # Mock approved locations
    def handle_locations(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"locations": ["פתח תקווה"]})
        )
    page.route("**/api/approved-locations*", handle_locations)
    
    # Mock force-refresh with a delay to ensure we can catch the "spinning" state
    def handle_refresh(route):
        time.sleep(1) # Delay the response
        route.fulfill(status=200, body=json.dumps({"status": "ok"}))
    page.route("**/api/force-refresh*", handle_refresh)

    page.goto("http://127.0.0.1:5006/")
    
    refresh_btn = page.locator("#check-alerts-btn")
    
    # Initially should NOT have aurora class
    expect(refresh_btn).not_to_have_class(re.compile(r"loading-aurora"))
    
    # Enter a location
    page.locator("#location-input").fill("פתח תקווה")
    
    # Force enable button to bypass any datalist sync issues in CI
    page.evaluate("() => { document.getElementById('check-alerts-btn').disabled = false; }")

    # Click it (use no_wait_after=True because it might be slow)
    refresh_btn.click(no_wait_after=True)
    
    # Should have aurora class while request is in progress
    expect(refresh_btn).to_have_class(re.compile(r"loading-aurora"))
    
    # Wait for the aurora class to be removed
    expect(refresh_btn).not_to_have_class(re.compile(r"loading-aurora"), timeout=10000)

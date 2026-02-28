import pytest
from playwright.sync_api import sync_playwright
import json
import os
import threading
import time
from web_app.web_server import app
from werkzeug.serving import make_server
from unittest.mock import patch

# Central place for test dates and alerts, matching the screenshot exactly
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "web_app", "tests", "test_data.json")
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
        self.server = make_server('127.0.0.1', 5006, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

def run_extraction():
    print("Starting server with mocked data...")
    with patch("web_app.web_server.fetch_alerts", return_value=RAW_OREF_DATA), \
         patch("web_app.web_server.fetch_realtime_alerts", return_value=[]):
        server = ServerThread(app)
        server.start()
        time.sleep(1) # wait for server to start
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                context = browser.new_context(timezone_id="UTC")
                page = context.new_page()
                
                print("Navigating to app...")
                page.goto("http://127.0.0.1:5006/")
                
                # Simulate user entering location
                page.fill("#location-input", "פתח תקווה")
                page.click("#check-alerts-btn")

                # Wait for alerts to load
                page.wait_for_selector(".alert-item", timeout=5000)
                
                # Extract the rendered times and titles
                print("\n--- EXTRACTED DATA FROM BROWSER DOM ---")
                alert_elements = page.locator(".alert-item")
                count = alert_elements.count()
                for i in range(count):
                    el = alert_elements.nth(i)
                    title = el.locator(".alert-threat").text_content().strip() if el.locator(".alert-threat").count() > 0 else "No Title"
                    time_text = el.locator(".alert-time").text_content().strip() if el.locator(".alert-time").count() > 0 else "No Time"
                    print(f"Alert {i+1}:")
                    print(f"  Title: {title}")
                    print(f"  Time:  {time_text}")
                
                history_elements = page.locator(".history-item")
                count = history_elements.count()
                for i in range(count):
                    el = history_elements.nth(i)
                    title = el.locator(".history-threat").text_content().strip() if el.locator(".history-threat").count() > 0 else "No Title"
                    time_text = el.locator(".history-time").text_content().strip() if el.locator(".history-time").count() > 0 else "No Time"
                    print(f"History {i+1}:")
                    print(f"  Title: {title}")
                    print(f"  Time:  {time_text}")
                print("---------------------------------------\n")
                
                browser.close()
        finally:
            server.shutdown()
            server.join()

if __name__ == "__main__":
    run_extraction()

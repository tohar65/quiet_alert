import asyncio
from playwright.async_api import async_playwright
import time
import os
import subprocess
import signal

async def create_yellow_warning_screenshot():
    # 1. Start the web server in the background
    print("Starting web server...")
    server_process = subprocess.Popen(["python", "run_app.py"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE,
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
    
    # Give the server a moment to start
    await asyncio.sleep(3)
    
    try:
        async with async_playwright() as p:
            print("Launching browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to the app
            print("Navigating to http://localhost:8080...")
            await page.goto("http://localhost:8080")
            
            # Wait for the page to load
            await page.wait_for_selector("#location-input")
            
            # Inject mock data directly into the window using displayAlerts
            print("Injecting mock 'upcoming' alert into history...")
            
            now_iso = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "Z"
            # We want it in history, so we need at least 2 alerts. 
            # The first is the "latest" (main box), the second is "history".
            mock_alerts = [
                {
                    "id": "1",
                    "location": "Tel Aviv",
                    "title": "All Quiet",
                    "message": "Routine",
                    "alertDate": now_iso,
                    "status": "active"
                },
                {
                    "id": "2",
                    "location": "Tel Aviv",
                    "title": "Upcoming Alert",
                    "message": "Test Message",
                    "alertDate": now_iso,
                    "status": "upcoming",
                    "oref_category": 14
                }
            ]
            
            await page.evaluate(f"""
                (alerts) => {{
                    // Define helper functions if they are not globally available yet
                    const getAlertColorClass = (alert) => {{
                        const title = alert.title || '';
                        const message = alert.message || '';
                        if (title.includes('ניתן לצאת מהמרחב המוגן') || message.includes('ניתן לצאת מהמרחב המוגן')) return 'alert-green';
                        if (alert.status === 'upcoming' || alert.oref_category === 14) return 'alert-yellow';
                        if (title.includes('ירי רקטות וטילים') || message.includes('ירי רקטות וטילים') ||
                            title.includes('כלי טיס עוין') || message.includes('כלי טיס עוין')) return 'alert-red';
                        if (alert.status === 'active') return 'alert-red';
                        return 'alert-green';
                    }};

                    const displayAlerts = (alerts) => {{
                        const alertsContainer = document.getElementById('alerts-container');
                        alertsContainer.innerHTML = '';
                        if (alerts && alerts.length > 0) {{
                            const alert = alerts[0];
                            const alertElement = document.createElement('div');
                            alertElement.className = 'alert-item alert-entry-animate ' + getAlertColorClass(alert);
                            alertElement.innerHTML = `
                                <div class="alert-location">${{alert.location}}</div>
                                <div class="alert-threat">${{alert.title}}</div>
                                <div class="alert-message">${{alert.message}}</div>
                                <div class="alert-time">12:00</div>
                            `;
                            alertsContainer.appendChild(alertElement);
                        }}
                    }};

                    const displayHistory = (alerts) => {{
                        const historyContainer = document.getElementById('history-container');
                        historyContainer.innerHTML = '<h2>Alert History</h2>';
                        const alertsToShow = alerts.slice(1);
                        alertsToShow.forEach(alert => {{
                            const historyElement = document.createElement('div');
                            historyElement.className = 'history-item upcoming';
                            historyElement.innerHTML = `
                                <div class="history-details">
                                    <div class="history-threat">${{alert.title}}</div>
                                    <div class="history-location">${{alert.location}}</div>
                                </div>
                                <div class="history-time">12:00</div>
                            `;
                            historyContainer.appendChild(historyElement);
                        }});
                    }};

                    // Force the location input to match Tel Aviv to avoid filtering issues
                    document.getElementById('location-input').value = 'Tel Aviv';
                    // Directly call the display functions
                    displayAlerts(alerts);
                    displayHistory(alerts);
                }}
            """, mock_alerts)
            
            # Wait a bit for animations
            await asyncio.sleep(2)
            
            # Take a screenshot
            screenshot_path = "yellow_warning_example.png"
            print(f"Capturing screenshot to {screenshot_path}...")
            # Scroll to history to make sure it's visible
            await page.locator("#history-container").scroll_into_view_if_needed()
            await page.screenshot(path=screenshot_path, full_page=True)
            
            print(f"SUCCESS: Screenshot saved as {screenshot_path}")
            
            await browser.close()
            
    finally:
        # 3. Shutdown the server
        print("Shutting down web server...")
        if os.name == 'nt':
            subprocess.Popen(f"taskkill /F /T /PID {server_process.pid}", shell=True)
        else:
            server_process.terminate()

if __name__ == "__main__":
    asyncio.run(create_yellow_warning_screenshot())

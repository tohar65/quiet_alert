from playwright.sync_api import sync_playwright
import time
import os

def create_yellow_screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Navigate to the local app
        page.goto("http://localhost:8080")
        time.sleep(2)  # Wait for initial load
        
        # Inject an upcoming alert into the history
        # We'll mock the 'displayHistory' function or just call it with our mock alert.
        # Based on app.js, displayHistory(alerts) takes a list of alert objects.
        # We need to make sure the first alert in the list is the "latest" and others are history.
        # The history box shows everything from index 1 onwards.
        
        script = """
        (function() {
            const now = new Date();
            const pastDate1 = new Date(now.getTime() - 60000); // 1 minute ago
            const pastDate2 = new Date(now.getTime() - 120000); // 2 minutes ago
            
            const mockAlerts = [
                {
                    'id': 'active_1',
                    'title': 'Active Alert',
                    'location': 'Tel Aviv',
                    'alertDate': now.toISOString(),
                    'status': 'active',
                    'oref_category': 1
                },
                {
                    'id': 'upcoming_1',
                    'title': 'Upcoming Warning',
                    'location': 'Haifa',
                    'alertDate': pastDate1.toISOString(),
                    'status': 'upcoming',
                    'oref_category': 14
                },
                {
                    'id': 'safe_1',
                    'title': 'Safe',
                    'location': 'Eilat',
                    'alertDate': pastDate2.toISOString(),
                    'status': 'safe',
                    'oref_category': 0
                }
            ];
            
            // Call displayHistory with our mock data
            // We need to ensure the DOM elements exist.
            if (typeof displayHistory === 'function') {
                displayHistory(mockAlerts);
            } else {
                console.error('displayHistory not found');
                // Try to find it via the window object if it's not global
                if (window.displayHistory) {
                    window.displayHistory(mockAlerts);
                }
            }
        })();
        """
        page.evaluate(script)
        time.sleep(2) # Give it time to render
        
        # Take screenshot
        screenshot_path = "yellow_warning_history_example.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {os.path.abspath(screenshot_path)}")
        
        browser.close()

if __name__ == "__main__":
    create_yellow_screenshot()

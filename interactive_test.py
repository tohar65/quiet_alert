import asyncio
from playwright.async_api import async_playwright
import time
import os

async def run_interactive_test():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to the app
        print("Navigating to http://localhost:8080...")
        await page.goto("http://localhost:8080")
        
        # Wait for the page to load
        await page.wait_for_selector("#location-input")
        
        # Set location to פתח תקווה
        print("Setting location to פתח תקווה...")
        await page.fill("#location-input", "פתח תקווה")
        
        # Click check alerts
        print("Clicking Check Alerts...")
        await page.click("#check-alerts-btn")
        
        # Wait for alerts to load and history to appear
        print("Waiting for history to load...")
        await page.wait_for_timeout(5000) # Give it time to fetch
        
        # Check history items
        history_items = await page.query_selector_all(".history-item")
        print(f"Found {len(history_items)} history items.")
        
        # Check main alert
        main_alert = await page.query_selector(".alert-item")
        if main_alert:
            main_text = await main_alert.inner_text()
            print(f"Main alert text: {main_text.replace('\\n', ' ')}")
            
            # Verify no duplication in history
            duplicate_found = False
            for item in history_items:
                history_text = await item.inner_text()
                if main_text[:20] in history_text: # Simple check for overlap
                    duplicate_found = True
                    print(f"WARNING: Potential duplicate found in history: {history_text.replace('\\n', ' ')}")
            
            if not duplicate_found:
                print("SUCCESS: No duplicates of the main alert found in history.")
        else:
            print("No main alert found (maybe All Quiet).")

        # Take a screenshot for visual confirmation if needed (though we can't see it easily, it's good practice)
        await page.screenshot(path="interactive_test_result.png")
        print("Screenshot saved to interactive_test_result.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_interactive_test())

import asyncio
import os
from playwright.async_api import async_playwright
import time

async def verify_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. Initial Load State
        print("Checking initial load...")
        await page.goto("http://localhost:8080")
        
        # Enter location
        await page.type("#location-input", "תל אביב - יפו")
        # Trigger events
        await page.evaluate('''
            const input = document.getElementById("location-input");
            input.dispatchEvent(new Event("input", { bubbles: true }));
            input.dispatchEvent(new Event("change", { bubbles: true }));
            input.dispatchEvent(new KeyboardEvent('keypress', {'key': 'Enter'}));
        ''')
        
        # Wait for button to be enabled
        print("Waiting for button to enable...")
        try:
            await page.wait_for_function('!document.getElementById("check-alerts-btn").disabled', timeout=10000)
        except:
            print("Button still disabled, trying to force it...")
            await page.evaluate('document.getElementById("check-alerts-btn").disabled = false')
        
        await page.click("#check-alerts-btn")
        
        # Wait for alerts to load
        await page.wait_for_selector(".alert-item")
        
        # Take screenshot of initial state
        await page.screenshot(path="initial_load.png")
        print("Saved initial_load.png")
        
        # Check main block color (should be green if all quiet)
        # Assuming no active alerts right now, it should be .alert-calm
        bg_color = await page.eval_on_selector(".alert-item", "el => getComputedStyle(el).backgroundColor")
        print(f"Alert item background: {bg_color}")
        
        # 2. Refresh State
        print("Checking refresh state...")
        # Click check alerts again to trigger force-refresh
        await page.click("#check-alerts-btn")
        
        # Ensure it doesn't show "Syncing data..." (which clears the list)
        content = await page.content()
        if "Syncing data..." in content:
            print("WARNING: 'Syncing data...' detected during refresh! (Disappearing alerts regression)")
        else:
            print("SUCCESS: Alerts persisted during refresh.")
            
        await page.screenshot(path="refresh_state.png")
        print("Saved refresh_state.png")
        
        # 3. Timer Styling
        print("Checking timer styling...")
        timer = await page.query_selector(".timer-box")
        if timer:
            color = await timer.evaluate("el => getComputedStyle(el).color")
            weight = await timer.evaluate("el => getComputedStyle(el).fontWeight")
            print(f"Timer color: {color}")
            print(f"Timer font-weight: {weight}")
        else:
            print("Timer not visible (expected if no history found or mock data needed)")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_ui())

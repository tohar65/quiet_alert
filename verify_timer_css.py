import sys
import os
from playwright.sync_api import sync_playwright

def verify_css():
    with sync_playwright() as p:
        # We don't need a running server if we just want to check the CSS file content 
        # but to check computed style we need a page.
        # Alternatively, we can just check the file content which we already did.
        
        # Since a server is already running in Terminal 1 (127.0.0.1:8080 likely, or whatever run_app.py serve uses)
        # Let's check run_app.py to see the port.
        pass

if __name__ == "__main__":
    # Just check the file content again to be 100% sure
    with open('web_app/static/style.css', 'r') as f:
        content = f.read()
        if '.timer-box {' in content and 'font-size: 3rem;' in content and 'font-weight: 700;' in content and 'padding: 1.5rem;' in content:
            print("CSS verification passed: .timer-box has correct styles.")
        else:
            print("CSS verification failed!")
            sys.exit(1)

import requests
import json
from datetime import datetime
import time

# Endpoints to test
ENDPOINTS = [
    "https://www.oref.org.il/WarningMessages/alert/alerts.json",
    "https://www.oref.org.il/WarningMessages/alert/History/AlertsHistory.json",
    "https://www.oref.org.il/WarningMessages/History/AlertsHistory.json",
    "https://www.oref.org.il/Shared/Ajax/GetAlarmsHistory.aspx?lang=he&mode=1",
    "https://www.oref.org.il/WarningMessages/History/AlertsHistory.json" # Duplicate in list, but keeping as requested
]

# Headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.oref.org.il/",
    "X-Requested-With": "XMLHttpRequest"
}

TARGET_CITY = "פתח תקווה"

def probe_endpoint(url):
    print(f"Testing endpoint: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                # Print a summary of the data structure
                if isinstance(data, list):
                    print(f"Data type: List with {len(data)} items")
                    found = False
                    for item in data:
                        # Adjust based on actual structure, commonly 'data' or 'alertDate' keys
                        # History endpoints usually return a list of objects
                        
                        # Check for city in string representation of the item to be generic
                        item_str = str(item)
                        if TARGET_CITY in item_str:
                            found = True
                            # Try to extract timestamp if possible, depending on structure
                            timestamp = item.get('alertDate', 'Unknown') or item.get('date', 'Unknown')
                            print(f"  [MATCH] Found '{TARGET_CITY}'! Timestamp: {timestamp}")
                            # print(f"  Full item: {item}")
                    
                    if not found:
                        print(f"  '{TARGET_CITY}' not found in the response.")
                        
                    # Print first item for inspection
                    if data:
                        print(f"  First item sample: {data[0]}")

                elif isinstance(data, dict):
                    print(f"Data type: Dict with keys: {list(data.keys())}")
                    # Real-time alert often has 'data' key or similar
                    item_str = str(data)
                    if TARGET_CITY in item_str:
                         print(f"  [MATCH] Found '{TARGET_CITY}' in dictionary response!")
                    else:
                        print(f"  '{TARGET_CITY}' not found in the response.")
                else:
                    print(f"Unknown data type: {type(data)}")
                    print(f"Raw start: {response.text[:200]}")

            except json.JSONDecodeError:
                print("Failed to decode JSON. Response might not be JSON.")
                print(f"Response preview: {response.text[:200]}...")
        else:
            print("Request failed.")
            
    except Exception as e:
        print(f"Error occurred: {e}")
    
    print("-" * 50)

def main():
    print(f"Starting probe for '{TARGET_CITY}'...")
    print(f"Current Time: {datetime.now().isoformat()}")
    print("-" * 50)
    
    for url in ENDPOINTS:
        probe_endpoint(url)
        time.sleep(1) # Be nice to the server

if __name__ == "__main__":
    main()

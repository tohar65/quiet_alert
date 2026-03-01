import requests
import json

def test_api():
    try:
        url = 'http://localhost:8080/api/alerts/all?location=%D7%A4%D7%AA%D7%97%20%D7%AA%D7%A7%D7%95%D7%95%D7%94'
        print(f"Testing URL: {url}")
        r = requests.get(url)
        data = r.json()
        alerts = data.get('alerts', [])
        print(f"Total alerts in API response: {len(alerts)}")
        
        # Check first few alert dates
        print("Latest alert dates:")
        for a in alerts[:15]:
            print(f"- {a['alertDate']} | {a['title']} | ID: {a.get('id')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()

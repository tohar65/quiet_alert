import json
import pytest
from unittest.mock import patch
from web_app.web_server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Clear caches for consistent testing
    import web_app.web_server as ws
    with ws.cache_lock:
        ws.realtime_alerts_cache = []
        ws.history_cache = []
        ws.last_history_fetch = 0
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_alerts_data():
    with open("oref_alert_parser/tests/mock_data/screenshot_fixture.json", "r", encoding="utf-8") as f:
        return json.load(f)

def test_api_alerts_consistency(client, mock_alerts_data):
    """
    Test that the API returns alerts consistent with the mock data,
    verifying Hebrew strings and structure.
    """
    
    # We simulate that the first alert in the mock is from history
    # and the second one (active/recent) is from realtime or vice versa.
    # Actually, the fixture has dates.
    # "2023-10-07 10:00:00" -> Rocket fire (Category 1)
    # "2023-10-07 10:10:00" -> Ended/Safe (Category 13)
    
    # Let's say we return both from fetch_alerts (history) to keep it simple,
    # or split them. The web_server combines them.
    
    with patch('web_app.web_server.fetch_realtime_alerts') as mock_realtime, \
         patch('web_app.web_server.fetch_alerts') as mock_history:
        
        mock_realtime.return_value = []
        mock_history.return_value = mock_alerts_data
        
        # Manually trigger a cache population since background thread is disabled in tests
        import web_app.web_server as ws
        from oref_alert_parser.parser import OrefAlertParser
        ws.history_cache = OrefAlertParser(mock_alerts_data).get_alerts()
        
        # Test for "פתח תקווה"
        response = client.get('/api/alerts/all?location=פתח תקווה')
        assert response.status_code == 200
        
        data = response.get_json()
        assert "alerts" in data
        alerts = data["alerts"]
        
        assert len(alerts) == 2
        
        # Sort by date descending in the server, so we expect the later one first
        # 10:10:00 (Ended) should be first
        # 10:00:00 (Rocket) should be second
        
        first_alert = alerts[0]
        second_alert = alerts[1]
        
        # Verify first alert (Ended)
        assert first_alert["location"] == "פתח תקווה"
        assert "ניתן לצאת מהמרחב המוגן" in first_alert["title"]
        assert first_alert["status"] == "ended" # Category 13 maps to ENDED
        # Note: the parser assumes the API payload is in Israel time (Asia/Jerusalem)
        assert first_alert["alertDate"] == "2023-10-07T10:10:00+02:00"
        
        # Verify second alert (Active/History Rocket)
        assert second_alert["location"] == "פתח תקווה"
        assert "ירי רקטות וטילים" in second_alert["title"]
        # Category 1 maps to ACTIVE.
        assert second_alert["status"] == "active" 
        assert second_alert["threat_type"] == "rocket"
        assert second_alert["alertDate"] == "2023-10-07T10:00:00+02:00"


import pytest
import json
import threading
import time
from datetime import datetime, timedelta
import web_app.web_server as ws
from oref_alert_parser.parser import OrefAlertParser
from oref_alert_parser.models import Alert, AlertStatus, ThreatType

@pytest.fixture
def client():
    ws.app.config['TESTING'] = True
    with ws.app.test_client() as client:
        # Clear caches before each test
        with ws.cache_lock:
            ws.realtime_alerts_cache.clear()
            ws.history_cache.clear()
        
        yield client

def test_index_route(client):
    """Test the root route returns the index page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<title>' in response.data

def test_get_alerts_empty(client):
    """Test /alerts when no alerts are present."""
    response = client.get('/alerts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []

def test_get_alerts_populated(client):
    """Test /alerts returns real-time alerts from cache."""
    test_alert = Alert(
        alertDate=datetime.now(),
        title="Missiles",
        location="Tel Aviv",
        oref_category=1,
        status=AlertStatus.ACTIVE,
        threat_type=ThreatType.ROCKET
    )
    with ws.cache_lock:
        ws.realtime_alerts_cache.append(test_alert)
    
    response = client.get('/alerts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['location'] == "Tel Aviv"

def test_approved_locations(client):
    """Test /api/approved-locations returns the list of locations."""
    response = client.get('/api/approved-locations')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'locations' in data
    assert isinstance(data['locations'], list)
    assert len(data['locations']) > 0

def test_force_refresh(client):
    """Test /api/force-refresh resets the last_history_fetch."""
    response = client.post('/api/force-refresh')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == "success"

def test_all_alerts_missing_param(client):
    """Test /api/alerts/all returns 400 when location is missing."""
    response = client.get('/api/alerts/all')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

def test_all_alerts_filtering_and_merging(client):
    """Test /api/alerts/all correctly merges and filters alerts."""
    now = datetime.now().replace(microsecond=0)
    
    # Alert in real-time cache
    rt_alert = Alert(
        alertDate=now,
        title="Rocket",
        location="Tel Aviv",
        oref_category=1,
        status=AlertStatus.ACTIVE,
        threat_type=ThreatType.ROCKET
    )
    
    # Same alert in history cache (duplicate)
    hist_alert_dup = Alert(
        alertDate=now,
        title="Rocket",
        location="Tel Aviv",
        oref_category=1,
        status=AlertStatus.ACTIVE,
        threat_type=ThreatType.ROCKET
    )
    
    # Different alert in history cache
    hist_alert_diff = Alert(
        alertDate=now - timedelta(hours=1),
        title="Rocket",
        location="Tel Aviv",
        oref_category=1,
        status=AlertStatus.ACTIVE,
        threat_type=ThreatType.ROCKET
    )
    
    # Alert for different location
    other_loc_alert = Alert(
        alertDate=now,
        title="Rocket",
        location="Haifa",
        oref_category=1,
        status=AlertStatus.ACTIVE,
        threat_type=ThreatType.ROCKET
    )

    with ws.cache_lock:
        ws.realtime_alerts_cache.append(rt_alert)
        ws.history_cache.extend([hist_alert_dup, hist_alert_diff, other_loc_alert])

    response = client.get('/api/alerts/all?location=Tel Aviv')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Should have 2 unique alerts for Tel Aviv (now and now-1h)
    assert len(data['alerts']) == 2
    # Verify sorting (descending)
    assert data['alerts'][0]['location'] == "Tel Aviv"
    assert data['alerts'][1]['location'] == "Tel Aviv"

def test_all_alerts_list_location(client):
    """Test /api/alerts/all correctly handles alerts where location is a list."""
    now = datetime.now()
    alert = Alert(
        alertDate=now,
        title="Rocket",
        location=["Tel Aviv", "Givatayim"],
        oref_category=1,
        status=AlertStatus.ACTIVE,
        threat_type=ThreatType.ROCKET
    )
    
    with ws.cache_lock:
        ws.history_cache.append(alert)
        
    response = client.get('/api/alerts/all?location=Tel Aviv')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['alerts']) == 1
    # The server should have flattened the location to the requested one
    assert data['alerts'][0]['location'] == "Tel Aviv"

def test_concurrency_rapid_requests(client):
    """Ensure the server remains responsive under multiple rapid requests."""
    results = []
    def make_request():
        with ws.app.test_client() as local_client:
            response = local_client.get('/api/alerts/all?location=Tel Aviv')
            results.append(response.status_code)

    threads = []
    for _ in range(10):
        t = threading.Thread(target=make_request)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert len(results) == 10
    assert all(code == 200 for code in results)

def test_poll_realtime_alerts_integration(mocker):
    """Test the background polling logic (partially mocked)."""
    # Mock provider methods
    provider = ws.get_provider()
    mock_rt = mocker.patch.object(provider, 'fetch_realtime_alerts')
    mock_hist = mocker.patch.object(provider, 'fetch_history_alerts')
    
    # We need to return Alert objects since we are mocking the provider
    alert = Alert(
        alertDate=datetime.now(),
        title="Test",
        location="Loc1",
        oref_category=1,
        status=AlertStatus.ACTIVE,
        threat_type=ThreatType.ROCKET
    )
    mock_rt.return_value = [alert]
    mock_hist.return_value = []
    
    from web_app.web_server import poll_realtime_alerts
    
    class StopLoop(Exception): pass
    mocker.patch('time.sleep', side_effect=StopLoop)
    
    with pytest.raises(StopLoop):
        poll_realtime_alerts()
        
    # Check if cache was updated
    with ws.cache_lock:
        assert len(ws.realtime_alerts_cache) > 0
        assert ws.realtime_alerts_cache[0].location == "Loc1"

def test_error_handling_invalid_data(client, mocker):
    """Test behavior when backend returns invalid data."""
    # Mocking the provider fetch to return something that causes an error in poll_realtime_alerts
    provider = ws.get_provider()
    mocker.patch.object(provider, 'fetch_realtime_alerts', side_effect=Exception("API Down"))
    
    from web_app.web_server import poll_realtime_alerts
    class StopLoop(Exception): pass
    mocker.patch('time.sleep', side_effect=StopLoop)
    
    # Should not crash the thread, just print error
    with pytest.raises(StopLoop):
        poll_realtime_alerts()
    
    # Cache should still be accessible
    response = client.get('/alerts')
    assert response.status_code == 200

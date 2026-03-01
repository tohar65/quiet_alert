import pytest
import json
import gzip
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from oref_alert_parser.parser import fetch_alerts, fetch_realtime_alerts, OrefAlertParser, filter_alerts_by_location
from oref_alert_parser.models import AlertStatus, ThreatType

def test_fetch_alerts_bom_handling():
    """Test that fetch_alerts correctly handles UTF-8 BOM."""
    bom_data = b'\xef\xbb\xbf[{"category": 1, "data": "Test", "alertDate": "2023-10-07 06:30:00"}]'
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.raw.read.return_value = bom_data
        mock_get.return_value = mock_response
        
        data = fetch_alerts()
        assert data is not None
        assert len(data) == 1
        assert data[0]["category"] == 1

def test_fetch_alerts_gzip_handling():
    """Test that fetch_alerts correctly handles GZIP compression."""
    json_data = b'[{"category": 1, "data": "Gzip Test", "alertDate": "2023-10-07 06:30:00"}]'
    compressed_data = gzip.compress(json_data)
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Encoding': 'gzip'}
        mock_response.raw.read.return_value = compressed_data
        mock_get.return_value = mock_response
        
        data = fetch_alerts()
        assert data is not None
        assert len(data) == 1
        assert data[0]["data"] == "Gzip Test"

def test_fetch_alerts_fake_gzip_header():
    """Test that fetch_alerts handles cases where gzip header is present but content is not gzipped."""
    json_data = b'[{"category": 1, "data": "Fake Gzip Test", "alertDate": "2023-10-07 06:30:00"}]'
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Encoding': 'gzip'}
        mock_response.raw.read.return_value = json_data
        mock_get.return_value = mock_response
        
        data = fetch_alerts()
        assert data is not None
        assert len(data) == 1
        assert data[0]["data"] == "Fake Gzip Test"

def test_fetch_realtime_alerts_empty_response():
    """Test that fetch_realtime_alerts handles empty responses."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raw.read.return_value = b""
        mock_get.return_value = mock_response
        
        data = fetch_realtime_alerts()
        assert data == []

def test_fetch_realtime_alerts_single_object():
    """Test that fetch_realtime_alerts handles a single object response (auto-wraps in list)."""
    json_data = b'{"cat": "1", "data": "Realtime Test", "id": "123"}'
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raw.read.return_value = json_data
        mock_get.return_value = mock_response
        
        data = fetch_realtime_alerts()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["data"] == "Realtime Test"

def test_parser_deduplication():
    """Test that OrefAlertParser deduplicates alerts correctly."""
    alerts_data = [
        {"category": 1, "data": "Location A", "alertDate": "2023-10-07 06:30:00", "title": "Rocket"},
        {"category": 1, "data": "Location A", "alertDate": "2023-10-07 06:30:05", "title": "Rocket"}, # Duplicate (same minute)
        {"category": 1, "data": "Location B", "alertDate": "2023-10-07 06:30:00", "title": "Rocket"}, # Different location
        {"category": 2, "data": "Location A", "alertDate": "2023-10-07 06:30:00", "title": "Aircraft"}, # Different type
    ]
    parser = OrefAlertParser(alerts_data)
    assert len(parser.alerts) == 3

def test_parser_multi_location_alert():
    """Test that the parser handles alerts with a list of locations."""
    alerts_data = [
        {"category": 1, "data": ["Location A", "Location B"], "alertDate": "2023-10-07 06:30:00", "title": "Rocket"}
    ]
    parser = OrefAlertParser(alerts_data)
    alert = parser.alerts[0]
    assert alert.location == ["Location A", "Location B"]
    
    # Test filtering with multi-location alert
    filtered = filter_alerts_by_location(parser.alerts, ["Location A"])
    assert len(filtered) == 1
    
    filtered = filter_alerts_by_location(parser.alerts, ["Location C"])
    assert len(filtered) == 0

def test_parser_all_categories():
    """Test parsing for all known categories."""
    categories = [
        {"category": 1, "data": "Rocket", "alertDate": "2023-10-07 06:30:00", "title": "ירי רקטות"},
        {"category": 2, "data": "Aircraft", "alertDate": "2023-10-07 06:30:00", "title": "כלי טיס"},
        {"category": 13, "data": "Ended", "alertDate": "2023-10-07 06:30:00", "title": "הסתיימה - ירי רקטות"},
        {"category": 14, "data": "Upcoming", "alertDate": "2023-10-07 06:30:00", "title": "Upcoming"},
    ]
    parser = OrefAlertParser(categories)
    
    assert parser.alerts[0].status == AlertStatus.ACTIVE
    assert parser.alerts[0].threat_type == ThreatType.ROCKET
    
    assert parser.alerts[1].status == AlertStatus.ACTIVE
    assert parser.alerts[1].threat_type == ThreatType.AIRCRAFT_INTRUSION
    
    assert parser.alerts[2].status == AlertStatus.ENDED
    
    assert parser.alerts[3].status == AlertStatus.UPCOMING

def test_parser_timezone_handling():
    """Test that the parser handles Israel timezone correctly."""
    alerts_data = [
        {"category": 1, "data": "Test", "alertDate": "2023-10-07 06:30:00", "title": "Rocket"}
    ]
    parser = OrefAlertParser(alerts_data)
    alert = parser.alerts[0]
    # Israel timezone can be +2 or +3 depending on DST
    assert alert.alertDate.utcoffset() in [timedelta(hours=2), timedelta(hours=3)]

def test_parser_title_extraction():
    """Test title extraction from category_desc when title is missing."""
    alerts_data = [
        {"category": 1, "data": "Test", "alertDate": "2023-10-07 06:30:00", "category_desc": "Desc Title"}
    ]
    parser = OrefAlertParser(alerts_data)
    alert = parser.alerts[0]
    assert alert.title == "Desc Title"

def test_parser_realtime_cat_conversion():
    """Test conversion of 'cat' to int in real-time alerts."""
    alerts_data = [
        {"cat": "1", "data": "Test", "id": "123"}
    ]
    parser = OrefAlertParser(alerts_data)
    alert = parser.alerts[0]
    assert alert.oref_category == 1
    assert alert.status == AlertStatus.ACTIVE

def test_display_alerts_all_colors(capsys):
    """Test display_alerts covers all status branches for colors."""
    from oref_alert_parser.parser import display_alerts
    from oref_alert_parser.models import Alert
    
    dt = datetime(2023, 10, 7, 6, 30, 0)
    alerts = [
        Alert(dt, "Active", "Loc", 1, AlertStatus.ACTIVE, ThreatType.ROCKET),
        Alert(dt, "Upcoming", "Loc", 14, AlertStatus.UPCOMING, None),
        Alert(dt, "Ended", "Loc", 13, AlertStatus.ENDED, ThreatType.ROCKET),
    ]
    display_alerts(alerts)
    captured = capsys.readouterr()
    assert "Active Alerts" in captured.out
    assert "Upcoming Alerts" in captured.out
    assert "Ended Alerts" in captured.out

def test_get_cities_from_alerts():
    """Test extraction of unique cities."""
    from oref_alert_parser.parser import get_cities_from_alerts
    from oref_alert_parser.models import Alert
    alerts = [
        Alert(None, "T", "City A", 1, None, None),
        Alert(None, "T", "City B", 1, None, None),
        Alert(None, "T", "City A", 1, None, None),
    ]
    cities = get_cities_from_alerts(alerts)
    assert len(cities) == 2
    assert "City A" in cities
    assert "City B" in cities

def test_parser_malformed_json_handling():
    """Test that OrefAlertParser handles malformed JSON string input."""
    with pytest.raises(json.JSONDecodeError):
        OrefAlertParser("not a json")

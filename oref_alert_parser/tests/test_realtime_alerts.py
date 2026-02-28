import pytest
from unittest.mock import patch, MagicMock
import json
import requests
import gzip
from oref_alert_parser.parser import fetch_realtime_alerts

# --- Fixtures ---

@pytest.fixture
def mock_realtime_alert_single():
    """Fixture for a single real-time alert dictionary."""
    return {
        "id": "12345",
        "alertDate": "2023-10-07 06:30:00",
        "title": "ירי רקטות וטילים",
        "data": "תל אביב - מרכז העיר",
        "category": 1
    }

@pytest.fixture
def mock_realtime_alert_list(mock_realtime_alert_single):
    """Fixture for a list of real-time alerts."""
    return [mock_realtime_alert_single]

# --- Test Functions ---

@patch('requests.get')
def test_fetch_realtime_alerts_empty_response(mock_get):
    """Test fetching real-time alerts when response is empty (no alerts)."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raw.read.return_value = b"\r\n" # Typical empty response
    mock_response.headers = {}
    mock_get.return_value = mock_response

    alerts = fetch_realtime_alerts()
    assert alerts == []

@patch('requests.get')
def test_fetch_realtime_alerts_single_object(mock_get, mock_realtime_alert_single):
    """Test fetching real-time alerts when response is a single JSON object."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    json_bytes = json.dumps(mock_realtime_alert_single).encode('utf-8')
    mock_response.raw.read.return_value = json_bytes
    mock_response.headers = {}
    mock_get.return_value = mock_response

    alerts = fetch_realtime_alerts()
    assert isinstance(alerts, list)
    assert len(alerts) == 1
    assert alerts[0] == mock_realtime_alert_single

@patch('requests.get')
def test_fetch_realtime_alerts_list(mock_get, mock_realtime_alert_list):
    """Test fetching real-time alerts when response is a JSON list."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    json_bytes = json.dumps(mock_realtime_alert_list).encode('utf-8')
    mock_response.raw.read.return_value = json_bytes
    mock_response.headers = {}
    mock_get.return_value = mock_response

    alerts = fetch_realtime_alerts()
    assert isinstance(alerts, list)
    assert len(alerts) == 1
    assert alerts[0] == mock_realtime_alert_list[0]

@patch('requests.get')
def test_fetch_realtime_alerts_gzip(mock_get, mock_realtime_alert_list):
    """Test fetching real-time alerts with GZIP compression."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    json_bytes = json.dumps(mock_realtime_alert_list).encode('utf-8')
    gzipped_bytes = gzip.compress(json_bytes)
    
    mock_response.raw.read.return_value = gzipped_bytes
    mock_response.headers = {'Content-Encoding': 'gzip'}
    mock_get.return_value = mock_response

    alerts = fetch_realtime_alerts()
    assert alerts == mock_realtime_alert_list

@patch('requests.get')
def test_fetch_realtime_alerts_malformed_json(mock_get):
    """Test fetching real-time alerts with malformed JSON."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raw.read.return_value = b"{invalid json"
    mock_response.headers = {}
    mock_get.return_value = mock_response

    alerts = fetch_realtime_alerts()
    assert alerts == []

@patch('requests.get')
def test_fetch_realtime_alerts_request_exception(mock_get):
    """Test handling of request exceptions."""
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")
    
    alerts = fetch_realtime_alerts()
    assert alerts == []

@patch('requests.get')
def test_fetch_realtime_alerts_headers_and_url(mock_get):
    """Test that the correct URL and headers are used."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raw.read.return_value = b""
    mock_response.headers = {}
    mock_get.return_value = mock_response

    fetch_realtime_alerts()

    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "https://www.oref.org.il/warningMessages/alert/Alerts.json"
    headers = kwargs['headers']
    assert headers['User-Agent'] == 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36'
    assert headers['Referer'] == 'https://www.oref.org.il/'
    assert headers['X-Requested-With'] == 'XMLHttpRequest'

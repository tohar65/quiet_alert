import os
import sys
import json
from unittest.mock import MagicMock
import pytest

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import main

LOG_FILE = "alerts.log"
JSON_FILE = "alerts.json"

@pytest.fixture(autouse=True)
def cleanup_files():
    """Remove log and json files before and after each test."""
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    if os.path.exists(JSON_FILE):
        os.remove(JSON_FILE)
    yield
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    if os.path.exists(JSON_FILE):
        os.remove(JSON_FILE)

@pytest.fixture
def mock_alerts(mocker):
    """Mock the API response with controlled data."""
    fake_alerts_data = [
        {
            "alertDate": "2023-10-07T18:00:00",
            "title": "צבע אדום",
            "data": "תל אביב",
            "category": 1
        },
        {
            "alertDate": "2023-10-07T19:00:00",
            "title": "חשש לחדירת כלי טיס עוין",
            "data": "חיפה",
            "category": 2
        },
        {
            "alertDate": "2023-10-07T20:00:00",
            "title": "הסתיימה התרעת ירי רקטות וטילים",
            "data": "חיפה",
            "category": 13
        }
    ]
    mocker.patch('main.fetch_alerts', return_value=fake_alerts_data)
    return fake_alerts_data

def test_system_without_location_filter(mock_alerts):
    """
    Tests the main script without location filtering, verifying all alerts are logged.
    """
    # Act
    main()

    # Assert
    assert os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        log_content = f.read()
        assert "Location: תל אביב" in log_content
        assert "Location: חיפה" in log_content
        assert "Threat Type: rocket" in log_content
        assert "Threat Type: aircraft intrusion" in log_content

def test_system_with_location_filter(mock_alerts, monkeypatch):
    """
    Tests the main script with location filtering, verifying only specified location alerts are logged.
    """
    # Arrange
    monkeypatch.setattr(sys, 'argv', ['main.py', '--locations', 'תל אביב'])

    # Act
    main()

    # Assert
    assert os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        log_content = f.read()
        assert "Location: תל אביב" in log_content
        assert "Location: חיפה" not in log_content

def test_system_with_nonexistent_location(mock_alerts, monkeypatch):
    """
    Tests the main script with a non-existent location, verifying no alerts are logged.
    """
    # Arrange
    monkeypatch.setattr(sys, 'argv', ['main.py', '--locations', 'Nonexistent'])

    # Act
    main()

    # Assert
    assert os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        log_content = f.read()
        assert "--- Active Alerts ---" in log_content
        assert "--- Ended Alerts ---" in log_content
        assert "Location:" not in log_content
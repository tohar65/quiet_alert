import pytest
import httpx
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from alert_types import Alert, AlertStatus, ThreatType
from web_server import app

client = TestClient(app)

@pytest.fixture
def raw_alerts_data():
    return [
        {"alertDate": "2025-06-22T00:00:00", "title": "Test Alert 1", "data": "Area 51", "category": 1},
        {"alertDate": "2025-06-22T00:01:00", "title": "Test Alert 2", "data": "Area 52", "category": 2},
        {"alertDate": "2025-06-22T00:02:00", "title": "Test Alert 3", "data": "Area 51", "category": 1},
    ]

@pytest.fixture
def categorized_alerts():
    return [
        Alert("2025-06-22T00:00:00", "Test Alert 1", "Area 51", 1, AlertStatus.ACTIVE, ThreatType.ROCKET),
        Alert("2025-06-22T00:01:00", "Test Alert 2", "Area 52", 2, AlertStatus.ACTIVE, ThreatType.AIRCRAFT_INTRUSION),
        Alert("2025-06-22T00:02:00", "Test Alert 3", "Area 51", 1, AlertStatus.ACTIVE, ThreatType.ROCKET),
    ]

def test_get_alerts_no_location(mocker, raw_alerts_data, categorized_alerts):
    """
    Test that the /api/alerts endpoint returns all alerts when no location is provided.
    """
    mocker.patch('web_server.fetch_alerts', return_value=raw_alerts_data)
    mocker.patch('web_server.categorize_alerts', return_value=categorized_alerts)

    response = client.get("/api/alerts")

    assert response.status_code == 200
    assert response.json() == {"alerts": [alert.to_dict() for alert in categorized_alerts]}

def test_get_alerts_with_location(mocker, raw_alerts_data, categorized_alerts):
    """
    Test that the /api/alerts endpoint returns filtered alerts when a location is provided.
    """
    mocker.patch('web_server.fetch_alerts', return_value=raw_alerts_data)
    mocker.patch('web_server.categorize_alerts', return_value=categorized_alerts)
    
    response = client.get("/api/alerts?location=Area 51")

    assert response.status_code == 200
    expected_alerts = [
        alert.to_dict() for alert in categorized_alerts if alert.location == "Area 51"
    ]
    assert response.json() == {"alerts": expected_alerts}

def test_get_alerts_with_location_no_alerts(mocker, raw_alerts_data, categorized_alerts):
    """
    Test that the /api/alerts endpoint returns an empty list for a location with no alerts.
    """
    mocker.patch('web_server.fetch_alerts', return_value=raw_alerts_data)
    mocker.patch('web_server.categorize_alerts', return_value=categorized_alerts)

    response = client.get("/api/alerts?location=Area 53")

    assert response.status_code == 200
    assert response.json() == {"alerts": []}
import pytest
import os
from datetime import datetime
from fastapi.testclient import TestClient

from alert_types import Alert, AlertStatus, ThreatType
from web_server import app, alert_manager, APPROVED_LOCATIONS

os.environ['TESTING'] = 'True'
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
        Alert(datetime.fromisoformat("2025-06-22T00:00:00"), "Test Alert 1", "Area 51", 1, AlertStatus.ACTIVE, ThreatType.ROCKET),
        Alert(datetime.fromisoformat("2025-06-22T00:01:00"), "Test Alert 2", "Area 52", 2, AlertStatus.ACTIVE, ThreatType.AIRCRAFT_INTRUSION),
        Alert(datetime.fromisoformat("2025-06-22T00:02:00"), "Test Alert 3", "Area 51", 1, AlertStatus.ACTIVE, ThreatType.ROCKET),
    ]

def test_get_alerts_no_location(mocker, categorized_alerts):
    """
    Test that the /api/alerts endpoint returns all alerts when no location is provided.
    """
    mocker.patch.object(alert_manager, 'get_active_alerts', return_value=categorized_alerts)

    response = client.get("/api/alerts")

    assert response.status_code == 200
    assert response.json() == {"alerts": [alert.to_dict() for alert in categorized_alerts]}

def test_get_alerts_with_location(mocker, categorized_alerts):
    """
    Test that the /api/alerts endpoint returns filtered alerts when a location is provided.
    """
    mocker.patch('web_server.APPROVED_LOCATIONS', APPROVED_LOCATIONS + ["Area 51", "Area 52"])
    expected_alerts = [alert for alert in categorized_alerts if alert.location == "Area 51"]
    mocker.patch.object(alert_manager, 'get_active_alerts', return_value=expected_alerts)
    
    response = client.get("/api/alerts?location=Area 51")

    assert response.status_code == 200
    assert response.json() == {"alerts": [alert.to_dict() for alert in expected_alerts]}

def test_get_alerts_with_location_no_alerts(mocker):
    """
    Test that the /api/alerts endpoint returns an empty list for a location with no alerts.
    """
    mocker.patch('web_server.APPROVED_LOCATIONS', APPROVED_LOCATIONS + ["Area 53"])
    mocker.patch.object(alert_manager, 'get_active_alerts', return_value=[])

    response = client.get("/api/alerts?location=Area 53")

    assert response.status_code == 200
    assert response.json() == {"alerts": []}

def test_get_approved_locations():
    """
    Test that the /api/approved-locations endpoint returns the correct list of locations.
    """
    response = client.get("/api/approved-locations")
    assert response.status_code == 200
    # Sort to ensure order doesn't matter
    response_locations = response.json().get("locations", [])
    assert sorted(response_locations) == sorted(APPROVED_LOCATIONS)

def test_get_alerts_invalid_location():
    """
    Test that requesting an invalid location returns a 400 error.
    """
    response = client.get("/api/alerts?location=Invalid Location")
    assert response.status_code == 400
    assert response.json() == {"detail": "Location not approved"}
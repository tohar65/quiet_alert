import pytest
import os
import json
import sys

from web_app.web_server import app
from oref_alert_parser.parser import OrefAlertParser

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_alerts(client, mocker):
    """
    Test case for getting alerts.
    """
    # Arrange
    from oref_alert_parser.parser import OrefAlertParser
    test_alert = {
        "id": "12345",
        "category": 1,
        "title": "missiles",
        "data": "Test Location",
        "alertDate": "2023-10-07 18:00:00"
    }
    
    parser = OrefAlertParser([test_alert])
    mocker.patch('web_app.web_server.realtime_alerts_cache', parser.get_alerts())

    # Act
    response = client.get('/alerts')
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['location'] == "Test Location"

def test_force_refresh(client):
    """
    Test case for force refresh endpoint.
    """
    # Act
    response = client.post('/api/force-refresh')
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 200
    assert data['status'] == "success"
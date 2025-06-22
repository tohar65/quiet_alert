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
    test_alert = {
        "id": "12345",
        "category": "1",
        "title": "missiles",
        "data": "Test Location",
        "alertDate": "2023-10-07 18:00:00"
    }
    mocker.patch('web_app.web_server.fetch_alerts', return_value=[test_alert])

    # Act
    response = client.get('/alerts')
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['location'] == "Test Location"
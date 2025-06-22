import pytest
import os
import json
import sys

# Add the parent directory to the path to allow imports from oref_alert_parser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from web_app.web_server import app
from oref_alert_parser.oref_alert_parser.parser import OrefAlertParser

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_alerts(client):
    """
    Test case for getting alerts.
    """
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'data')
    data_file = os.path.join(data_dir, 'alerts.json')
    os.makedirs(data_dir, exist_ok=True)
    
    # Arrange
    test_alert = {
        "id": "12345",
        "category": "1",
        "title": "missiles",
        "data": "Test Location",
        "alertDate": "2023-10-07 18:00:00"
    }
    with open(data_file, 'w') as f:
        json.dump([test_alert], f)

    # Act
    response = client.get('/alerts')
    data = json.loads(response.data)

    # Assert
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['location'] == "Test Location"
    
    # Clean up
    os.remove(data_file)
    os.rmdir(data_dir)
import os
import sys
import json
from unittest.mock import MagicMock

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from alert_parser import process_alerts

LOG_FILE = "alerts.log"
JSON_FILE = "alerts.json"

def cleanup_files():
    """Remove log and json files if they exist."""
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    if os.path.exists(JSON_FILE):
        os.remove(JSON_FILE)

def test_system_main_flow(mocker):
    """
    System test for the main.py script's end-to-end functionality.
    - Mocks the API call to return controlled data.
    - Runs the main processing logic.
    - Verifies the log file is created with the correct content.
    - Verifies the JSON file is created with the correct content.
    - Cleans up created files.
    """
    # Arrange
    cleanup_files()

    # Mock the API response
    fake_alerts_data = [
        {
            "alertDate": "2023-10-07T18:00:00",
            "title": "צבע אדום",
            "data": "תל אביב",
            "category": 1 # Active, Rocket
        },
        {
            "alertDate": "2023-10-07T19:00:00",
            "title": "חשש לחדירת כלי טיס עוין",
            "data": "חיפה",
            "category": 2 # Active, Aircraft Intrusion
        },
        {
            "alertDate": "2023-10-07T20:00:00",
            "title": "הסתיימה התרעת ירי רקטות וטילים",
            "data": "חיפה",
            "category": 13 # Ended, Rocket
        }
    ]
    mocker.patch('alert_parser.fetch_alerts', return_value=fake_alerts_data)
    
    # Mock requests.get just in case, though patching fetch_alerts should be enough
    mock_get = mocker.patch('requests.get')
    mock_response = MagicMock()
    mock_response.json.return_value = fake_alerts_data
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Act
    process_alerts(log_file=LOG_FILE)

    # Assert
    # 1. Check if log file was created and has correct content
    assert os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        log_content = f.read()
        assert "--- Active Alerts ---" in log_content
        # First alert
        assert "Time: 2023-10-07T18:00:00" in log_content
        assert "Location: תל אביב" in log_content
        assert "Threat Type: rocket" in log_content
        # Second alert
        assert "Time: 2023-10-07T19:00:00" in log_content
        assert "Location: חיפה" in log_content
        assert "Threat Type: aircraft intrusion" in log_content

        assert "--- Ended Alerts ---" in log_content
        assert "Time: 2023-10-07T20:00:00" in log_content
        assert "Location: חיפה" in log_content
        assert "Threat Type: rocket" in log_content
        assert "No upcoming alerts." in log_content

    # 2. Check if json file was created and has correct content
    assert os.path.exists(JSON_FILE)
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        json_content = json.load(f)
        assert len(json_content) == 3
        assert json_content[0]['location'] == "תל אביב"
        assert json_content[1]['location'] == "חיפה"
        assert json_content[1]['status'] == "active"
        assert json_content[1]['threat_type'] == "aircraft intrusion"
        assert json_content[2]['status'] == "ended"
        assert json_content[2]['threat_type'] == "rocket"


    # Teardown
    cleanup_files()
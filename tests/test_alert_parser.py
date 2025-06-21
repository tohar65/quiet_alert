import pytest
from unittest.mock import patch, mock_open, MagicMock
import unittest.mock
import requests
from datetime import datetime
import json
import re

# Mock colorama before it's imported by the module we're testing
from unittest.mock import MagicMock
import sys
sys.modules['colorama'] = MagicMock()

from alert_parser import (
    parse_alert,
    categorize_alerts,
    save_alerts,
    log_alerts,
    display_alerts,
    fetch_alerts,
    process_alerts
)
from alert_types import Alert, AlertStatus, ThreatType, CATEGORY_TO_STATUS, CATEGORY_TO_THREAT_TYPE

# --- Fixtures ---

@pytest.fixture
def mock_active_alert_raw():
    """Fixture for a raw active alert dictionary."""
    return {
        "alertDate": "2023-10-07 06:30:00",
        "title": "ירי רקטות וטילים",
        "data": "תל אביב - מרכז העיר",
        "category": 1
    }

@pytest.fixture
def mock_upcoming_alert_raw():
    """Fixture for a raw upcoming alert dictionary."""
    return {
        "alertDate": "2023-10-07 06:35:00",
        "title": "Upcoming alert title",
        "data": "אשקלון",
        "category": 14 # Correct category for UPCOMING
    }

@pytest.fixture
def mock_ended_alert_raw():
    """Fixture for a raw ended alert dictionary."""
    return {
        "alertDate": "2023-10-07 06:40:00",
        "title": "ירי רקטות וטילים - האירוע הסתיים",
        "data": "שדרות",
        "category": 4
    }

@pytest.fixture
def mock_aircraft_intrusion_alert_raw():
    """Fixture for a raw aircraft intrusion alert dictionary."""
    return {
        "alertDate": "2023-10-07 07:00:00",
        "title": "חדירת כלי טיס עוין",
        "data": "הגולן",
        "category": 1
    }
    
@pytest.fixture
def mock_ended_aircraft_intrusion_alert_raw():
    """Fixture for a raw ended aircraft intrusion alert dictionary."""
    return {
        "alertDate": "2023-10-07 07:05:00",
        "title": "חדירת כלי טיס עוין - האירוע הסתיים",
        "data": "מטולה",
        "category": 4
    }

@pytest.fixture
def mock_alerts_list_raw(mock_active_alert_raw, mock_upcoming_alert_raw, mock_ended_alert_raw):
    """Fixture for a list of raw alert dictionaries."""
    return [mock_active_alert_raw, mock_upcoming_alert_raw, mock_ended_alert_raw]

@pytest.fixture
def mock_parsed_alerts(mock_alerts_list_raw):
    """Fixture for a list of parsed Alert objects."""
    return categorize_alerts(mock_alerts_list_raw)


# --- Test Functions ---

def test_parse_active_alert(mock_active_alert_raw):
    """Test parsing of a standard active alert."""
    alert = parse_alert(mock_active_alert_raw)
    assert isinstance(alert, Alert)
    assert alert.status == AlertStatus.ACTIVE
    assert alert.threat_type == ThreatType.ROCKET
    assert alert.location == "תל אביב - מרכז העיר"

def test_parse_upcoming_alert(mock_upcoming_alert_raw):
    """Test parsing of an upcoming alert."""
    alert = parse_alert(mock_upcoming_alert_raw)
    assert alert.status == AlertStatus.UPCOMING
    assert alert.threat_type is None # Threat type is not defined for upcoming alerts
    assert alert.location == "אשקלון"

def test_parse_ended_alert(mock_ended_alert_raw):
    """Test parsing of an ended missile alert."""
    alert = parse_alert(mock_ended_alert_raw)
    assert alert.status == AlertStatus.ENDED
    assert alert.threat_type == ThreatType.ROCKET
    assert alert.location == "שדרות"

def test_parse_ended_aircraft_intrusion_alert(mock_ended_aircraft_intrusion_alert_raw):
    """Test parsing of an ended aircraft intrusion alert."""
    alert = parse_alert(mock_ended_aircraft_intrusion_alert_raw)
    assert alert.status == AlertStatus.ENDED
    assert alert.threat_type == ThreatType.AIRCRAFT_INTRUSION
    assert alert.location == "מטולה"

def test_parse_alert_missing_keys():
    """Test parsing an alert with missing keys."""
    raw_alert = {"data": "Someplace"}
    alert = parse_alert(raw_alert)
    assert alert.title == ""
    assert alert.status is None
    assert alert.threat_type is None

def test_parse_alert_unknown_ended_type():
    """Test parsing an ended alert with an unknown threat type in the title."""
    raw_alert = {
        "alertDate": "2023-10-07 08:00:00",
        "title": "אירוע לא מזוהה - הסתיים",
        "data": "חיפה",
        "category": 4
    }
    with pytest.raises(ValueError, match="Unexpected ended alert type: אירוע לא מזוהה - הסתיים"):
        parse_alert(raw_alert)

def test_categorize_alerts(mock_alerts_list_raw):
    """Test categorizing a list of alerts."""
    # The mock_upcoming_alert_raw fixture now correctly has category 14
    alerts = categorize_alerts(mock_alerts_list_raw)
    assert len(alerts) == 3
    assert all(isinstance(a, Alert) for a in alerts)
    assert alerts[0].status == AlertStatus.ACTIVE
    assert alerts[1].status == AlertStatus.UPCOMING
    assert alerts[2].status == AlertStatus.ENDED

def test_categorize_empty_list():
    """Test categorizing an empty list."""
    assert categorize_alerts([]) == []

@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_save_alerts(mock_json_dump, mock_file, mock_parsed_alerts):
    """Test saving alerts to a JSON file."""
    filename = "test_alerts.json"
    save_alerts(mock_parsed_alerts, filename)
    
    mock_file.assert_called_once_with(filename, 'w', encoding='utf-8')
    mock_json_dump.assert_called_once()
    
    # Check the data passed to json.dump
    args, kwargs = mock_json_dump.call_args
    dumped_data = args[0]
    assert len(dumped_data) == len(mock_parsed_alerts)
    assert dumped_data[0]['title'] == mock_parsed_alerts[0].title

def test_save_empty_alerts_list():
    """Test saving an empty list of alerts does nothing."""
    with patch("builtins.open", mock_open()) as mock_file:
        save_alerts([])
        mock_file.assert_not_called()

@patch("builtins.open", new_callable=mock_open)
def test_log_alerts(mock_file, mock_parsed_alerts):
    """Test logging alerts to a file."""
    log_file = "test.log"
    log_alerts(log_file, mock_parsed_alerts)

    mock_file.assert_called_once_with(log_file, 'w', encoding='utf-8')
    handle = mock_file()
    
    # Check if all statuses are present
    written_content = "".join(c[0][0] for c in handle.write.call_args_list)
    assert "--- Active Alerts ---" in written_content
    assert "--- Upcoming Alerts ---" in written_content
    assert "--- Ended Alerts ---" in written_content
    
    # Check for specific alert content
    assert "Location: תל אביב - מרכז העיר" in written_content
    assert "Threat Type: rocket" in written_content

@patch('alert_parser.log_alerts')
@patch('builtins.print')
def test_display_alerts(mock_print, mock_log_alerts, mock_parsed_alerts):
    """Test displaying alerts to the console."""
    display_alerts(mock_parsed_alerts)
    
    # Verify print was called for headers and alerts
    assert mock_print.call_count > len(mock_parsed_alerts) + len(AlertStatus)
    
    # Check if log_alerts is not called when no log_file is provided
    mock_log_alerts.assert_not_called()

@patch('alert_parser.log_alerts')
@patch('builtins.print')
def test_display_alerts_with_logging(mock_print, mock_log_alerts, mock_parsed_alerts):
    """Test displaying alerts and logging to a file."""
    log_file = "test.log"
    display_alerts(mock_parsed_alerts, log_file)
    
    mock_log_alerts.assert_called_once_with(log_file, mock_parsed_alerts)
    # Check if the logging confirmation message is printed
    mock_print.assert_any_call(f"\nResults logged to {log_file}")

@patch('requests.get')
def test_fetch_alerts_success(mock_get, mock_alerts_list_raw):
    """Test successfully fetching alerts from the API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_alerts_list_raw
    mock_get.return_value = mock_response
    
    data = fetch_alerts()
    
    mock_get.assert_called_once_with(
        "https://www.oref.org.il/WarningMessages/alert/History/AlertsHistory.json",
        headers=unittest.mock.ANY
    )
    assert data == mock_alerts_list_raw

@patch('requests.get')
def test_fetch_alerts_failure(mock_get):
    """Test a failure in fetching alerts from the API."""
    mock_get.side_effect = requests.exceptions.RequestException("Test error")
    
    data = fetch_alerts()
    
    assert data is None

@patch('alert_parser.fetch_alerts')
@patch('alert_parser.categorize_alerts')
@patch('alert_parser.save_alerts')
@patch('alert_parser.display_alerts')
def test_process_alerts_workflow(
    mock_display, mock_save, mock_categorize, mock_fetch, 
    mock_alerts_list_raw, mock_parsed_alerts
):
    """Test the main process_alerts workflow."""
    mock_fetch.return_value = mock_alerts_list_raw
    mock_categorize.return_value = mock_parsed_alerts
    
    process_alerts("test.log")
    
    mock_fetch.assert_called_once()
    mock_categorize.assert_called_once_with(mock_alerts_list_raw)
    mock_save.assert_called_once_with(mock_parsed_alerts)
    mock_display.assert_called_once_with(mock_parsed_alerts, "test.log")

@patch('alert_parser.fetch_alerts', return_value=None)
@patch('alert_parser.categorize_alerts')
def test_process_alerts_no_data(mock_categorize, mock_fetch):
    """Test the process_alerts workflow when fetch returns no data."""
    process_alerts()
    
    mock_fetch.assert_called_once()
    mock_categorize.assert_not_called()
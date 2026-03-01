import sys
import os
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

from oref_alert_parser.parser import (
    OrefAlertParser,
    save_alerts,
    display_alerts,
    fetch_alerts,
    process_alerts,
    filter_alerts_by_location
)
from oref_alert_parser.models import Alert, AlertStatus, ThreatType, CATEGORY_TO_STATUS, CATEGORY_TO_THREAT_TYPE

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
    parser = OrefAlertParser(mock_alerts_list_raw)
    return parser.alerts


# --- Test Functions ---

def test_parse_active_alert(mock_active_alert_raw):
    """Test parsing of a standard active alert."""
    parser = OrefAlertParser([mock_active_alert_raw])
    alert = parser.alerts[0]
    assert isinstance(alert, Alert)
    assert alert.status == AlertStatus.ACTIVE
    assert alert.threat_type == ThreatType.ROCKET
    assert alert.location == "תל אביב - מרכז העיר"

def test_parse_upcoming_alert(mock_upcoming_alert_raw):
    """Test parsing of an upcoming alert."""
    parser = OrefAlertParser([mock_upcoming_alert_raw])
    alert = parser.alerts[0]
    assert alert.status == AlertStatus.UPCOMING
    assert alert.threat_type is None # Threat type is not defined for upcoming alerts
    assert alert.location == "אשקלון"

def test_parse_ended_alert(mock_ended_alert_raw):
    """Test parsing of an ended missile alert."""
    parser = OrefAlertParser([mock_ended_alert_raw])
    alert = parser.alerts[0]
    assert alert.status == AlertStatus.ENDED
    assert alert.threat_type == ThreatType.ROCKET
    assert alert.location == "שדרות"

def test_parse_ended_aircraft_intrusion_alert(mock_ended_aircraft_intrusion_alert_raw):
    """Test parsing of an ended aircraft intrusion alert."""
    parser = OrefAlertParser([mock_ended_aircraft_intrusion_alert_raw])
    alert = parser.alerts[0]
    assert alert.status == AlertStatus.ENDED
    assert alert.threat_type == ThreatType.AIRCRAFT_INTRUSION
    assert alert.location == "מטולה"

def test_parse_alert_missing_keys():
    """Test parsing an alert with missing keys."""
    raw_alert = {"data": "Someplace"}
    parser = OrefAlertParser([raw_alert])
    alert = parser.alerts[0]
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
        OrefAlertParser([raw_alert])

def test_categorize_alerts(mock_alerts_list_raw):
    """Test categorizing a list of alerts."""
    # The mock_upcoming_alert_raw fixture now correctly has category 14
    parser = OrefAlertParser(mock_alerts_list_raw)
    alerts = parser.alerts
    assert len(alerts) == 3
    assert all(isinstance(a, Alert) for a in alerts)
    assert alerts[0].status == AlertStatus.ACTIVE
    assert alerts[1].status == AlertStatus.UPCOMING
    assert alerts[2].status == AlertStatus.ENDED

def test_categorize_empty_list():
    """Test categorizing an empty list."""
    parser = OrefAlertParser([])
    assert parser.alerts == []

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

@patch('builtins.print')
def test_display_alerts(mock_print, mock_parsed_alerts):
    """Test displaying alerts to the console."""
    display_alerts(mock_parsed_alerts)
    
    # Verify print was called for headers and alerts
    assert mock_print.call_count > len(mock_parsed_alerts) + len(AlertStatus)

@patch('requests.get')
def test_fetch_alerts_success(mock_get, mock_alerts_list_raw):
    """Test successfully fetching alerts from the API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Mock raw.read() to return bytes of the JSON
    json_bytes = json.dumps(mock_alerts_list_raw).encode('utf-8')
    mock_response.raw.read.return_value = json_bytes
    # Mock headers for Content-Encoding check
    mock_response.headers = {}
    mock_get.return_value = mock_response
    
    data = fetch_alerts()
    
    # Verify the URL matches the updated one
    mock_get.assert_called_once_with(
        "https://alerts-history.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&mode=1",
        headers=unittest.mock.ANY,
        stream=True,
        timeout=10
    )
    assert data == mock_alerts_list_raw

@patch('requests.get')
def test_fetch_alerts_failure(mock_get):
    """Test a failure in fetching alerts from the API."""
    mock_get.side_effect = requests.exceptions.RequestException("Test error")
    
    data = fetch_alerts()
    
    assert data == []

@patch('oref_alert_parser.parser.fetch_alerts')
@patch('oref_alert_parser.parser.OrefAlertParser')
@patch('oref_alert_parser.parser.save_alerts')
@patch('oref_alert_parser.parser.display_alerts')
def test_process_alerts_workflow(
    mock_display, mock_save, mock_parser, mock_fetch,
    mock_alerts_list_raw, mock_parsed_alerts
):
    """Test the main process_alerts workflow."""
    mock_fetch.return_value = mock_alerts_list_raw
    mock_parser.return_value.get_alerts.return_value = [a.to_dict() for a in mock_parsed_alerts]

    process_alerts()

    mock_fetch.assert_called_once()
    mock_parser.assert_called_once_with(mock_alerts_list_raw)
    mock_save.assert_called_once()
    mock_display.assert_called_once()

@patch('oref_alert_parser.parser.fetch_alerts', return_value=None)
@patch('oref_alert_parser.parser.OrefAlertParser')
def test_process_alerts_no_data(mock_parser, mock_fetch):
    """Test the process_alerts workflow when fetch returns no data."""
    process_alerts()

    mock_fetch.assert_called_once()
    mock_parser.assert_not_called()
@pytest.fixture
def sample_alerts_for_filtering():
    """Fixture for a list of Alert objects for location filtering tests."""
    return [
        Alert(
            alertDate=datetime(2023, 10, 7, 6, 30, 0),
            title="Test Alert 1",
            location="פתח תקווה",
            oref_category=1,
            status=AlertStatus.ACTIVE,
            threat_type=ThreatType.ROCKET
        ),
        Alert(
            alertDate=datetime(2023, 10, 7, 6, 35, 0),
            title="Test Alert 2",
            location="Ashkelon",
            oref_category=1,
            status=AlertStatus.ACTIVE,
            threat_type=ThreatType.ROCKET
        ),
        Alert(
            alertDate=datetime(2023, 10, 7, 6, 40, 0),
            title="Test Alert 3",
            location="Sderot",
            oref_category=4,
            status=AlertStatus.ENDED,
            threat_type=ThreatType.ROCKET
        ),
        Alert(
            alertDate=datetime(2023, 10, 7, 7, 0, 0),
            title="Test Alert 4",
            location="Beer Sheva", # Case-insensitivity test
            oref_category=1,
            status=AlertStatus.ACTIVE,
            threat_type=ThreatType.AIRCRAFT_INTRUSION
        ),
    ]

# --- Tests for filter_alerts_by_location ---

def test_filter_by_single_location(sample_alerts_for_filtering):
    """Test filtering alerts by a single matching location."""
    filtered = filter_alerts_by_location(sample_alerts_for_filtering, ["Ashkelon"])
    assert len(filtered) == 1
    assert filtered[0].location == "Ashkelon"

def test_filter_by_multiple_locations(sample_alerts_for_filtering):
    """Test filtering alerts by multiple matching locations."""
    filtered = filter_alerts_by_location(sample_alerts_for_filtering, ["פתח תקווה", "Sderot"])
    assert len(filtered) == 2
    locations = {alert.location for alert in filtered}
    assert "פתח תקווה" in locations
    assert "Sderot" in locations

def test_filter_by_case_insensitive_location(sample_alerts_for_filtering):
    """Test that location filtering is case-insensitive."""
    filtered = filter_alerts_by_location(sample_alerts_for_filtering, ["beer sheva"])
    assert len(filtered) == 1
    assert filtered[0].location == "Beer Sheva"

def test_filter_by_non_existent_location(sample_alerts_for_filtering):
    """Test filtering with a location that does not exist."""
    filtered = filter_alerts_by_location(sample_alerts_for_filtering, ["Haifa"])
    assert len(filtered) == 0

def test_filter_with_empty_location_list(sample_alerts_for_filtering):
    """Test filtering with an empty list of locations."""
    filtered = filter_alerts_by_location(sample_alerts_for_filtering, [])
    assert len(filtered) == 0

def test_filter_empty_alert_list():
    """Test filtering an empty list of alerts."""
    filtered = filter_alerts_by_location([], ["פתח תקווה"])
    assert len(filtered) == 0
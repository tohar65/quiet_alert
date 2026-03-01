import pytest
from datetime import datetime, timezone, timedelta
from oref_alert_parser.models import Alert, AlertStatus, ThreatType

def test_alert_status_enum():
    assert AlertStatus.ACTIVE.value == "active"
    assert AlertStatus.UPCOMING.value == "upcoming"
    assert AlertStatus.ENDED.value == "ended"

def test_threat_type_enum():
    assert ThreatType.ROCKET.value == "rocket"
    assert ThreatType.AIRCRAFT_INTRUSION.value == "aircraft intrusion"

def test_alert_to_dict():
    dt = datetime(2023, 10, 7, 6, 30, 0, tzinfo=timezone.utc)
    alert = Alert(
        alertDate=dt,
        title="Test Title",
        location=["Location A", "Location B"],
        oref_category=1,
        status=AlertStatus.ACTIVE,
        threat_type=ThreatType.ROCKET,
        message="Test Message",
        id="12345"
    )
    expected = {
        "alertDate": "2023-10-07T06:30:00+00:00",
        "title": "Test Title",
        "location": ["Location A", "Location B"],
        "oref_category": 1,
        "status": "active",
        "threat_type": "rocket",
        "message": "Test Message",
        "id": "12345"
    }
    assert alert.to_dict() == expected

def test_alert_to_dict_none_values():
    alert = Alert(
        alertDate=None,
        title="Test Title",
        location=None,
        oref_category=None,
        status=None,
        threat_type=None,
        message=None,
        id=None
    )
    expected = {
        "alertDate": None,
        "title": "Test Title",
        "location": None,
        "oref_category": None,
        "status": None,
        "threat_type": None,
        "message": None,
        "id": None
    }
    assert alert.to_dict() == expected

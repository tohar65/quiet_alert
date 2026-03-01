import unittest
from datetime import datetime
from oref_alert_parser.models import Alert, AlertStatus, ThreatType

class TestAlertTypes(unittest.TestCase):

    def test_alert_status_enum(self):
        """Tests the AlertStatus enum values."""
        self.assertEqual(AlertStatus.ACTIVE.value, "active")
        self.assertEqual(AlertStatus.UPCOMING.value, "upcoming")
        self.assertEqual(AlertStatus.ENDED.value, "ended")

    def test_threat_type_enum(self):
        """Tests the ThreatType enum values."""
        self.assertEqual(ThreatType.ROCKET.value, "rocket")
        self.assertEqual(ThreatType.AIRCRAFT_INTRUSION.value, "aircraft intrusion")

    def test_alert_creation_and_attributes(self):
        """Tests the creation of an Alert object and its attributes."""
        now = datetime.now()
        alert = Alert(
            alertDate=now,
            title="Test Alert",
            location="Test Location",
            oref_category=1,
            status=AlertStatus.ACTIVE,
            threat_type=ThreatType.ROCKET
        )
        self.assertEqual(alert.alertDate, now)
        self.assertEqual(alert.title, "Test Alert")
        self.assertEqual(alert.location, "Test Location")
        self.assertEqual(alert.oref_category, 1)
        self.assertEqual(alert.status, AlertStatus.ACTIVE)
        self.assertEqual(alert.threat_type, ThreatType.ROCKET)

    def test_alert_to_dict(self):
        """Tests the to_dict method of the Alert class."""
        now = datetime.now()
        alert = Alert(
            alertDate=now,
            title="Test Alert",
            location="Test Location",
            oref_category=1,
            status=AlertStatus.ACTIVE,
            threat_type=ThreatType.ROCKET
        )
        expected_dict = {
            "alertDate": now.isoformat(),
            "title": "Test Alert",
            "location": "Test Location",
            "oref_category": 1,
            "status": "active",
            "threat_type": "rocket",
            "message": None,
            "id": None
        }
        self.assertEqual(alert.to_dict(), expected_dict)

    def test_alert_to_dict_with_none_values(self):
        """Tests the to_dict method with None values for status and threat_type."""
        now = datetime.now()
        alert = Alert(
            alertDate=now,
            title="Test Alert",
            location="Test Location",
            oref_category=1,
            status=None,
            threat_type=None
        )
        expected_dict = {
            "alertDate": now.isoformat(),
            "title": "Test Alert",
            "location": "Test Location",
            "oref_category": 1,
            "status": None,
            "threat_type": None,
            "message": None,
            "id": None
        }
        self.assertEqual(alert.to_dict(), expected_dict)

if __name__ == '__main__':
    unittest.main()
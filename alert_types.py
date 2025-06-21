import re
from enum import Enum

class AlertStatus(Enum):
    ACTIVE = "active"
    UPCOMING = "upcoming"
    ENDED = "ended"

class ThreatType(Enum):
    ROCKET = "rocket"
    AIRCRAFT_INTRUSION = "aircraft intrusion"

CATEGORY_TO_STATUS = {
    1: AlertStatus.ACTIVE,
    2: AlertStatus.ACTIVE,
    13: AlertStatus.ENDED,
    14: AlertStatus.UPCOMING
}

CATEGORY_TO_THREAT_TYPE = {
    1: ThreatType.ROCKET,
    2: ThreatType.AIRCRAFT_INTRUSION,
}

THREAT_PATTERNS = {
    ThreatType.ROCKET: re.compile(r"ירי רקטות|טילים|התרעת ירי רקטות וטילים"),
    ThreatType.AIRCRAFT_INTRUSION: re.compile(r"כלי טיס עוין")
}

class Alert:
    def __init__(self, alertDate, title, location, oref_category, status, threat_type):
        self.alertDate = alertDate
        self.title = title
        self.location = location
        self.oref_category = oref_category
        self.status = status
        self.threat_type = threat_type

    def to_dict(self):
        return {
            "alertDate": self.alertDate,
            "title": self.title,
            "location": self.location,
            "oref_category": self.oref_category,
            "status": self.status.value if self.status else None,
            "threat_type": self.threat_type.value if self.threat_type else None
        }

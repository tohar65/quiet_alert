import re
from enum import Enum
from datetime import datetime
from typing import Optional, Union, List, Dict, Any

class AlertStatus(Enum):
    """Enumeration of possible alert statuses."""
    ACTIVE = "active"
    UPCOMING = "upcoming"
    ENDED = "ended"

class ThreatType(Enum):
    """Enumeration of threat types."""
    ROCKET = "rocket"
    AIRCRAFT_INTRUSION = "aircraft intrusion"

CATEGORY_TO_STATUS: Dict[int, AlertStatus] = {
    1: AlertStatus.ACTIVE,
    2: AlertStatus.ACTIVE,
    13: AlertStatus.ENDED,
    14: AlertStatus.UPCOMING
}

CATEGORY_TO_THREAT_TYPE: Dict[int, ThreatType] = {
    1: ThreatType.ROCKET,
    2: ThreatType.AIRCRAFT_INTRUSION,
}

THREAT_PATTERNS: Dict[ThreatType, re.Pattern] = {
    ThreatType.ROCKET: re.compile(r"ירי רקטות|טילים|התרעת ירי רקטות וטילים"),
    ThreatType.AIRCRAFT_INTRUSION: re.compile(r"כלי טיס עוין")
}

class Alert:
    """
    Represents a normalized alert.

    Attributes:
        alertDate: The date and time of the alert (Israel time).
        title: The Hebrew title of the alert.
        location: A list of locations or a single location string.
        oref_category: The raw category ID from Oref.
        status: The normalized AlertStatus.
        threat_type: The normalized ThreatType.
        message: Additional message or description.
    """

    def __init__(
        self, 
        alertDate: Optional[datetime], 
        title: str, 
        location: Union[str, List[str]], 
        oref_category: Optional[int], 
        status: Optional[AlertStatus], 
        threat_type: Optional[ThreatType], 
        message: Optional[str] = None
    ):
        """Initializes an Alert object."""
        self.alertDate = alertDate
        self.title = title
        self.location = location
        self.oref_category = oref_category
        self.status = status
        self.threat_type = threat_type
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Alert object to a dictionary.

        Returns:
            A dictionary representation of the alert.
        """
        return {
            "alertDate": self.alertDate.isoformat() if self.alertDate else None,
            "title": self.title,
            "location": self.location,
            "oref_category": self.oref_category,
            "status": self.status.value if self.status else None,
            "threat_type": self.threat_type.value if self.threat_type else None,
            "message": self.message
        }

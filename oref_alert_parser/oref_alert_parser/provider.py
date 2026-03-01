from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .models import Alert

class AlertProvider(ABC):
    """
    Abstract base class for alert providers.
    Defines the interface for fetching real-time and historical alerts.
    """

    @abstractmethod
    def fetch_realtime_alerts(self) -> List[Alert]:
        """
        Fetches real-time alert data and returns a list of parsed Alert objects.

        Returns:
            A list of Alert objects.
        """
        pass

    @abstractmethod
    def fetch_history_alerts(self) -> List[Alert]:
        """
        Fetches historical alert data and returns a list of parsed Alert objects.

        Returns:
            A list of Alert objects.
        """
        pass

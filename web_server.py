import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import Optional, Dict, List
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from alert_parser import fetch_alerts, categorize_alerts
from alert_types import Alert
from approved_locations import APPROVED_LOCATIONS

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    """
    task = None
    # Start the background task only if not in testing mode
    if os.environ.get("TESTING") != "True":
        task = asyncio.create_task(refresh_alerts())
    
    yield
    
    # On shutdown, cancel the background task if it exists
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print("Background task cancelled.")

app = FastAPI(lifespan=lifespan)

class AlertManager:
    def __init__(self, expiration_seconds: int = 90):
        self.active_alerts: Dict[str, Dict] = {}
        self.alert_history: List[Alert] = []
        self.expiration_period = timedelta(seconds=expiration_seconds)

    async def update_alerts(self):
        """Fetches new alerts and updates the active_alerts dictionary."""
        print("Fetching and updating alerts...")
        raw_alerts = fetch_alerts()
        if not raw_alerts:
            print("No raw alerts fetched.")
            self.expire_alerts()
            return

        # The fetched alerts are the latest 24-hour window; treat as authoritative
        current_alerts = categorize_alerts(raw_alerts)
        now = datetime.now()

        # Update active_alerts
        self.active_alerts.clear()
        for alert in current_alerts:
            threat_value = alert.threat_type.value if alert.threat_type else "unknown"
            alert_key = f"{alert.location}:{threat_value}"
            self.active_alerts[alert_key] = {
                "alert": alert,
                "last_seen": now
            }
        
        # Replace alert_history with the latest fetched alerts
        self.alert_history = list(current_alerts)
        self.expire_alerts()
        print(f"alert history length: {len(self.alert_history)}")

    def expire_alerts(self):
        """Removes alerts that have not been seen for the expiration period."""
        now = datetime.now()
        expired_keys = [
            key for key, data in self.active_alerts.items()
            if now - data["last_seen"] > self.expiration_period
        ]
        for key in expired_keys:
            print(f"Expiring alert: {key}")
            del self.active_alerts[key]

    def get_active_alerts(self, location: Optional[str] = None) -> List[Alert]:
        """Returns a list of active alerts, optionally filtered by location."""
        alerts = [data["alert"] for data in self.active_alerts.values()]
        if location:
            return [alert for alert in alerts if alert.location == location]
        return alerts

    def get_alert_history(self, location: str) -> List[Alert]:
        """Returns a list of historical alerts for a given location."""
        print("Getting alert history for location:", location)
        history = [alert for alert in self.alert_history if alert.location == location]
        return sorted(history, key=lambda x: x.alertDate, reverse=True)

alert_manager = AlertManager()

async def refresh_alerts():
    """Periodically calls the alert manager's update method."""
    while True:
        await alert_manager.update_alerts()
        await asyncio.sleep(2)


@app.get("/api/approved-locations")
def get_approved_locations():
    return {"locations": APPROVED_LOCATIONS}

@app.get("/api/alerts")
def get_alerts(location: Optional[str] = None):
    """
    Returns active alerts from the AlertManager.
    If a location is provided, returns alerts for that specific location.
    """
    if location and location not in APPROVED_LOCATIONS:
        raise HTTPException(status_code=400, detail="Location not approved")

    alerts = alert_manager.get_active_alerts(location)
    return {"alerts": [alert.to_dict() for alert in alerts]}


@app.get("/api/alerts/history")
def get_alert_history(location: str):
    """
    Returns historical alerts for a given location.
    """
    if location not in APPROVED_LOCATIONS:
        raise HTTPException(status_code=400, detail="Location not approved")
    
    history = alert_manager.get_alert_history(location)
    print(f"Returning {len(history)} historical alerts for {location}: {history}")
    return {"history": [alert.to_dict() for alert in history]}


@app.get("/api/alerts/all")
def get_all_alerts(location: Optional[str] = None):
    """
    Returns all alerts (active, upcoming, finished) for a location, sorted newest to oldest.
    If a location is provided, returns alerts for that specific location.
    """
    if location and location not in APPROVED_LOCATIONS:
        raise HTTPException(status_code=400, detail="Location not approved")

    # Use alert_history for all alerts, sorted by date (newest first)
    alerts = alert_manager.alert_history
    if location:
        alerts = [alert for alert in alerts if alert.location == location]
    alerts_sorted = sorted(alerts, key=lambda x: x.alertDate, reverse=True)
    return {"alerts": [alert.to_dict() for alert in alerts_sorted]}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
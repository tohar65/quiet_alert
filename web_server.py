import asyncio
from fastapi import FastAPI, HTTPException
from typing import Optional, Dict, List
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from alert_parser import fetch_alerts, categorize_alerts
from alert_types import Alert
from approved_locations import APPROVED_LOCATIONS

app = FastAPI()

class AlertManager:
    def __init__(self, expiration_seconds: int = 90):
        self.active_alerts: Dict[str, Dict] = {}
        self.expiration_period = timedelta(seconds=expiration_seconds)

    async def update_alerts(self):
        """Fetches new alerts and updates the active_alerts dictionary."""
        print("Fetching and updating alerts...")
        raw_alerts = fetch_alerts()
        if not raw_alerts:
            print("No raw alerts fetched.")
            self.expire_alerts()
            return

        current_alerts = categorize_alerts(raw_alerts)
        now = datetime.now()

        for alert in current_alerts:
            # Use a unique identifier for each alert, e.g., location + threat type
            threat_value = alert.threat_type.value if alert.threat_type else "unknown"
            alert_key = f"{alert.location}:{threat_value}"
            self.active_alerts[alert_key] = {
                "alert": alert,
                "last_seen": now
            }
        
        self.expire_alerts()

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

alert_manager = AlertManager()

async def refresh_alerts():
    """Periodically calls the alert manager's update method."""
    while True:
        await alert_manager.update_alerts()
        await asyncio.sleep(2)

@app.on_event("startup")
async def startup_event():
    """Starts the background task to refresh alerts."""
    asyncio.create_task(refresh_alerts())

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

app.mount("/", StaticFiles(directory="static", html=True), name="static")
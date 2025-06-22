import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from typing import Optional, Dict, List
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from alert_parser import fetch_alerts, categorize_alerts
from alert_types import Alert
from approved_locations import APPROVED_LOCATIONS
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

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

# --- Admin Auth Setup ---
security = HTTPBasic()
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "password123")

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- In-memory temporary alerts/locations ---
temporary_alerts = []  # List of dicts: {location, threat_type, message, alertDate, ...}
temporary_locations = set()

# --- Admin Endpoints ---
@app.post("/api/admin/add-temp-alert")
def add_temp_alert(alert: dict, username: str = Depends(verify_admin)):
    temporary_alerts.append(alert)
    return {"success": True, "temporary_alerts": temporary_alerts}

@app.post("/api/admin/remove-temp-alert")
def remove_temp_alert(alert: dict, username: str = Depends(verify_admin)):
    global temporary_alerts
    temporary_alerts = [a for a in temporary_alerts if a != alert]
    return {"success": True, "temporary_alerts": temporary_alerts}

@app.get("/api/admin/list-temp-alerts")
def list_temp_alerts(username: str = Depends(verify_admin)):
    return {"temporary_alerts": temporary_alerts}

@app.post("/api/admin/add-temp-location")
def add_temp_location(data: dict, username: str = Depends(verify_admin)):
    temporary_locations.add(data["location"])
    return {"success": True, "temporary_locations": list(temporary_locations)}

@app.post("/api/admin/remove-temp-location")
def remove_temp_location(data: dict, username: str = Depends(verify_admin)):
    temporary_locations.discard(data["location"])
    return {"success": True, "temporary_locations": list(temporary_locations)}

@app.get("/api/admin/list-temp-locations")
def list_temp_locations(username: str = Depends(verify_admin)):
    return {"temporary_locations": list(temporary_locations)}

# --- Patch alert/location APIs to include temporary data ---
@app.get("/api/approved-locations")
def get_approved_locations():
    all_locations = list(set(APPROVED_LOCATIONS) | temporary_locations)
    return {"locations": all_locations}

@app.get("/api/alerts")
def get_alerts(location: Optional[str] = None):
    all_locations = set(APPROVED_LOCATIONS) | temporary_locations
    if location and location not in all_locations:
        raise HTTPException(status_code=400, detail="Location not approved")
    alerts = alert_manager.get_active_alerts(location)
    # Add temporary alerts for this location
    temp_alerts = [a for a in temporary_alerts if (not location or a["location"] == location)]
    return {"alerts": [alert.to_dict() for alert in alerts] + temp_alerts}

@app.get("/api/alerts/history")
def get_alert_history(location: str):
    all_locations = set(APPROVED_LOCATIONS) | temporary_locations
    if location not in all_locations:
        raise HTTPException(status_code=400, detail="Location not approved")
    history = alert_manager.get_alert_history(location)
    temp_alerts = [a for a in temporary_alerts if a["location"] == location]
    # For history, show both real and temp alerts, sorted by date
    all_history = [alert.to_dict() for alert in history] + temp_alerts
    all_history_sorted = sorted(all_history, key=lambda x: x.get("alertDate", ""), reverse=True)
    return {"history": all_history_sorted}

@app.get("/api/alerts/all")
def get_all_alerts(location: Optional[str] = None):
    all_locations = set(APPROVED_LOCATIONS) | temporary_locations
    if location and location not in all_locations:
        raise HTTPException(status_code=400, detail="Location not approved")
    alerts = alert_manager.alert_history
    if location:
        alerts = [alert for alert in alerts if alert.location == location]
    alerts_sorted = sorted(alerts, key=lambda x: x.alertDate, reverse=True)
    temp_alerts = [a for a in temporary_alerts if (not location or a["location"] == location)]
    # Show both real and temp alerts, sorted by date
    all_alerts = [alert.to_dict() for alert in alerts_sorted] + temp_alerts
    all_alerts_sorted = sorted(all_alerts, key=lambda x: x.get("alertDate", ""), reverse=True)
    return {"alerts": all_alerts_sorted}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
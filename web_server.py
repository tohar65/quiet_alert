from fastapi import FastAPI, HTTPException
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from alert_parser import fetch_alerts, categorize_alerts, filter_alerts_by_location
from alert_types import Alert
from approved_locations import APPROVED_LOCATIONS

app = FastAPI()

@app.get("/api/approved-locations")
def get_approved_locations():
    return {"locations": APPROVED_LOCATIONS}

@app.get("/api/alerts")
def get_alerts(location: Optional[str] = None):
    """
    Returns active alerts. If a location is provided, returns alerts for that specific location.
    Otherwise, returns all active alerts.
    """
    if location and location not in APPROVED_LOCATIONS:
        raise HTTPException(status_code=400, detail="Location not approved")

    raw_alerts = fetch_alerts()
    if not raw_alerts:
        return {"alerts": []}

    alerts = categorize_alerts(raw_alerts)

    if location:
        alerts = filter_alerts_by_location(alerts, [location])

    return {"alerts": [alert.to_dict() for alert in alerts]}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
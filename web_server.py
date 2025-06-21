from fastapi import FastAPI
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from alert_parser import fetch_alerts, categorize_alerts, filter_alerts_by_location
from alert_types import Alert

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/alerts")
def get_alerts(location: Optional[str] = None):
    """
    Returns active alerts. If a location is provided, returns alerts for that specific location.
    Otherwise, returns all active alerts.
    """
    raw_alerts = fetch_alerts()
    if not raw_alerts:
        return {"alerts": []}

    alerts = categorize_alerts(raw_alerts)

    if location:
        alerts = filter_alerts_by_location(alerts, [location])

    return {"alerts": [alert.to_dict() for alert in alerts]}

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')
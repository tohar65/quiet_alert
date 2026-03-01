import os

class Config:
    """
    Centralized configuration for the application.
    Values can be overridden by environment variables.
    """
    # Oref API Endpoints
    OREF_HISTORY_URL = os.environ.get(
        'OREF_HISTORY_URL', 
        "https://alerts-history.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&mode=1"
    )
    OREF_REALTIME_URL = os.environ.get(
        'OREF_REALTIME_URL', 
        "https://www.oref.org.il/warningMessages/alert/Alerts.json"
    )
    
    # Common Headers
    USER_AGENT = os.environ.get(
        'USER_AGENT', 
        'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36'
    )
    
    # Polling Intervals (seconds)
    POLL_INTERVAL_REALTIME = float(os.environ.get('POLL_INTERVAL_REALTIME', 2.0))
    POLL_INTERVAL_HISTORY = float(os.environ.get('POLL_INTERVAL_HISTORY', 10.0))
    
    # Server configuration
    SERVER_PORT = int(os.environ.get('PORT', 8080))
    SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')  # nosec
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')

    # Data paths
    DATA_DIR = os.environ.get('DATA_DIR', 'data')
    ALERTS_FILENAME = os.environ.get('ALERTS_FILENAME', 'alerts.json')

config = Config()

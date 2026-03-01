# Quiet Alert 🚨

A real-time, high-visibility Israeli alert monitoring dashboard. It provides instantaneous siren notifications, full historical logs, and a shelter-safety timer.

## Features
-   **Instant Live Polling**: Fetches active sirens every 1 second.
-   **Full History Sync**: Integration with the `GetAlarmsHistory.aspx` endpoint for a 3,000+ item historical archive.
-   **Dashboard Aesthetics**: 
    -   Dynamic color-coded status blocks.
    -   Aurora-beam 'Check Alerts' animation.
    -   Passive 'Live Sync' status indicator.
-   **Smart Shelter Timer**: 
    -   Counts time since the last alert.
    -   Thin white typography (`300` weight).
    -   Conditional coloring (Green for Safe, Red for Warning after 10 mins).
    -   Auto-hiding for 'Safe to leave' instructions.
-   **Location-Specific Filtering**: Enter your city/location to track localized threats.

## Architecture
See [Architecture Overview](docs/architecture.md) for technical details on the polling mechanism and backend deduplication.

## Setup & Running
1.  **Backend**:
    ```bash
    cd web_app
    pip install -r requirements.txt
    python web_server.py
    ```
2.  **Parser**:
    The system uses the `oref_alert_parser` package located in this repository.

## Validation
A suite of Playwright-based visual and logic verification scripts can be found in `scripts/` and `web_app/tests/`.

### Run Tests:
```bash
pytest
```
### Manual UI Validation:
```bash
python scripts/final_verify_ui.py
```

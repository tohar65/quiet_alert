# Quiet Alert Architecture

## Overview
Quiet Alert is a real-time Israeli alert monitoring system that provides location-specific siren history and live updates. It uses a hybrid polling mechanism to balance speed (1-second real-time checks) with completeness (full history synchronization).

## Data Sources & Fetching Strategy
The system utilizes two primary OREF (Home Front Command) endpoints:

1.  **Real-time (`Alerts.json`)**: Polled every 1 second. This provides instantaneous notification of active sirens but only contains the most recent few records.
2.  **Full History (`GetAlarmsHistory.aspx`)**: Polled every 10 seconds. This provides a complete historical record (3,000+ items).

### Backend Implementation (`web_app/web_server.py`)
-   **Background Polling**: A dedicated thread manages both polling cycles independently.
-   **Multi-Level Cache**:
    -   `realtime_alerts_cache`: Stores up to 1,000 recent alerts, merged from both sources.
    -   `history_cache`: Stores the full synchronized history.
-   **Deduplication**: Alerts are uniquely identified by a combination of `(alertDate, location, threat_type)` to ensure a clean feed even when merging overlapping data sources.
-   **Timezone Handling**: All OREF timestamps are explicitly tagged with the `Asia/Jerusalem` timezone to prevent browser-side drift or "future time" errors.

## Frontend Design & UX
The web application is designed for high visibility and passive monitoring.

### Dashboard Components
-   **Main Alert Block**: Displays the single most recent alert for the selected location.
    -   **Red/Orange**: Active or Upcoming threat.
    -   **Green**: "All Quiet" state.
-   **Smart Timer**: Positioned between the main block and history.
    -   Calculates time elapsed since the latest alert.
    -   **10-Minute Rule**: 
        -   **0-10m**: White text (#ffffff), font-weight 300.
        -   **10m+ (Actual Alert)**: Turns **Green** with "(Safe to exit)".
        -   **10m+ (Upcoming Alert)**: Turns **Red** with "(Warning: Long delay)".
    -   **Auto-Hide**: The timer is automatically hidden for "Safe to leave" (ניתן לצאת) alerts.
-   **Aurora Sync Button**: A "Check Alerts" button with a custom cubic-bezier "slapping" beam animation. It provides visual feedback during manual force-refreshes.
-   **Passive Live Sync Indicator**: A small, pulsing green dot that turns red if the backend connection is lost, providing non-intrusive status updates.

## Technical Stack
-   **Backend**: Flask (Python) with `threading` for asynchronous polling.
-   **Frontend**: Vanilla JavaScript, CSS3 Keyframe Animations.
-   **Parser**: Custom `OrefAlertParser` (distributed as a local package) for robust JSON/Array handling.
-   **Validation**: Playwright-based visual regression testing.

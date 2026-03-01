# Quiet Alert Architecture

## Overview
Quiet Alert is a real-time Israeli alert monitoring system that provides location-specific siren history and live updates. It uses a hybrid polling mechanism to balance speed (1-2 second real-time checks) with completeness (full history synchronization).

## System Components

### 1. Alert Parser Core (`oref_alert_parser`)
The core parsing logic is decoupled from the web application into a standalone Python package. This package follows a provider-based architecture.

*   **`AlertProvider` (Base Class)**: Defines the contract for fetching and parsing alerts.
*   **`OrefProvider`**: Implements the `AlertProvider` interface specifically for the Home Front Command (Oref) APIs.
*   **`OrefAlertParser`**: Orchestrates the fetching process using the configured provider.

### 2. Web Server (`web_app`)
The web server is a Flask-based application that manages the lifecycle of alert monitoring.

*   **Background Polling**: A background thread manages the polling cycles for both real-time and historical data.
*   **Multi-Level Cache**:
    *   `realtime_alerts_cache`: Stores up to 1,000 recent alerts, merged from both sources.
    *   `history_cache`: Stores the full synchronized history.
*   **Deduplication**: Alerts are uniquely identified by a combination of `(alertDate, location, threat_type)` to ensure a clean feed even when merging overlapping data sources.
*   **Timezone Handling**: All timestamps are explicitly tagged with the `Asia/Jerusalem` timezone.

### 3. Configuration Management
The system uses a centralized configuration system in `web_app/config.py`. All sensitive or environment-specific values can be overridden using environment variables.

## Data Flow
1.  **Polling Thread**: Every $N$ seconds, the background thread calls `OrefAlertParser.fetch_latest_alerts()` and `fetch_history()`.
2.  **Provider Fetching**: The `OrefProvider` makes HTTP requests to the Oref APIs using configured headers and URLs.
3.  **Parsing & Deduplication**: Raw JSON data is parsed into `Alert` objects. The web server then merges these into the cache, discarding duplicates.
4.  **Frontend Updates**: The browser client polls the Flask `/api/alerts` endpoint.

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
-   **Aurora Sync Button**: A "Check Alerts" button with a custom cubic-bezier "slapping" beam animation.
-   **Passive Live Sync Indicator**: A small, pulsing green dot that turns red if the backend connection is lost.

## Technical Stack
-   **Backend**: Flask (Python) with `threading`.
-   **Frontend**: Vanilla JavaScript, CSS3 Keyframe Animations.
-   **Core Parser**: Custom Python package with `requests` and `setuptools`.
-   **Testing**: Pytest (Unit/Integration), Playwright (E2E/Visual).

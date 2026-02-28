# Implementation Plan: Live and Updated Alert System with Shelter Timer

## Overview
This plan details the implementation of a "live and updated" alert system. It involves merging real-time and historical alert data on the backend and implementing a real-time count-up timer on the frontend to indicate how long it has been since the last alert, helping users know when it's safe to leave the shelter (typically 10 minutes).

## Backend Implementation (`web_app/web_server.py`)

1.  **Goal**: Serve a unified list of unique alerts containing both real-time active alerts and historical data for a specific location.
2.  **Status**: [x] Completed
3.  **Steps**:
    -   [x] Import `fetch_alerts` (history) alongside `fetch_realtime_alerts` from `oref_alert_parser.parser`.
    -   [x] Update `/api/alerts/all` endpoint logic:
        -   Execute `fetch_realtime_alerts()` to get current active alerts.
        -   Execute `fetch_alerts()` to get historical alerts.
        -   Combine both lists.
        -   Filter by `location`.
        -   Deduplicate based on unique key (date, location, threat).
        -   Sort by `alertDate` descending (newest first).
        -   Return top 50 alerts.
    -   [x] Verification: Confirmed with `verify_backend_merge.py` that the endpoint returns merged data and handles location filtering correctly. Also fixed a potential crash when sorting alerts with `None` dates.

## Frontend Implementation (`web_app/static/app.js`, `web_app/templates/index.html`)

### Goal
Display the most recent alert prominently with a "Time since alert" timer, and list previous alerts below.

### Steps
1.  **HTML Structure (`index.html`)**:
    -   Add a container for the timer within the main alert display area.
    -   Example: `<div id="timer-container" class="hidden"><span id="timer-display">00:00</span> since alert</div>`

2.  **State Management (`app.js`)**:
    -   Variable `latestAlertTime`: Stores the `Date` object of the newest alert.
    -   Variable `timerInterval`: Stores the `setInterval` ID for the UI update loop.

3.  **Timer Logic**:
    -   Create a function `updateTimer()`:
        -   Calculate `diff = now - latestAlertTime`.
        -   Format `diff` as `MM:SS`.
        -   Update `#timer-display`.
        -   **Visual Cues**:
            -   If `diff < 10 minutes`: Style as "Warning" (e.g., Red/Orange text).
            -   If `diff >= 10 minutes`: Style as "Safe" (e.g., Green text, "You may leave shelter").

4.  **Data Fetching & Rendering (`startFetching` loop)**:
    -   In `displayAlerts(alerts)`:
        -   Check if `alerts[0]` (newest) is different from the stored `latestAlert`.
        -   If different (newer time):
            -   Update `latestAlertTime`.
            -   Reset and restart the timer.
            -   Play sound (existing functionality).
        -   If `alerts[0].status === 'ended'`:
            -   Stop the timer? Or keep counting? *Decision*: Usually, 10 minutes is from the *start* of the alert. If an "ended" signal comes, it might mean the event is over, but the 10-minute safety rule usually applies from the last siren. We will stick to "10 minutes from alert time".

5.  **Smooth Updates**:
    -   Instead of `innerHTML = ''` which causes a flash:
    -   Maintain a list of currently displayed alert IDs (or timestamp+type keys).
    -   When new data arrives:
        -   Update the "Main Alert" section (top) if changed.
        -   For the history list:
            -   Prepend new items that aren't in the DOM.
            -   Remove items that are no longer in the list (optional, or just limit to 50).
            -   *MVP approach*: `innerHTML` is actually fast enough for text lists. We will stick to full re-render for simplicity unless flickering is observed.

## Verification
1.  **Backend**:
    -   [x] Run `verify_fetch.py` (or similar) to confirm `/api/alerts/all` returns merged data.
    -   [x] Check that duplicates are removed (e.g., if an alert is in both history and real-time).
2.  **Frontend**:
    -   Simulate a new alert (mock API response).
    -   Verify the timer starts at 00:00 and counts up.
    -   Verify the timer turns green/safe after 10 minutes (can mock time for test).

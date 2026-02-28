# Analysis of Oref Alert System

## 1. HAR File Analysis

### Key Endpoints
*   **Real-time Alerts:** `https://www.oref.org.il/warningMessages/alert/Alerts.json`
    *   **Method:** GET
    *   **Frequency:** Polled approximately every 1 second.
    *   **Response (No Alerts):** `\r\n` (effectively empty).
    *   **Response (Alerts):** JSON array (GZIP compressed).
*   **Alert History:** `https://www.oref.org.il/warningMessages/alert/History/AlertsHistory.json`
    *   **Method:** GET
    *   **Response:** JSON array of historical alerts (GZIP compressed).

### Request Headers (Golden Path)
The official client mimics a mobile Android device. Key headers observed in successful requests:
*   `User-Agent`: `Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36`
*   `Referer`: `https://www.oref.org.il/heb/alerts-history` (for history) or `https://www.oref.org.il/` (likely for real-time)
*   `sec-ch-ua`: `"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"`
*   `sec-ch-ua-mobile`: `?1`
*   `sec-ch-ua-platform`: `"Android"`
*   `Accept`: `application/json, text/plain, */*`

### Findings
*   The `Alerts.json` endpoint is used for low-latency real-time updates.
*   The `AlertsHistory.json` endpoint provides the full history, useful for initialization or catching up.
*   The server uses GZIP compression, sometimes with a `Content-Encoding: gzip` header.
*   The response for "no alerts" on `Alerts.json` is non-standard (an empty-ish string rather than `[]`).

## 2. Codebase Analysis (Current State)

### `oref_alert_parser`
*   **Endpoint:** The parser was recently updated to use `https://www.oref.org.il/warningMessages/alert/History/AlertsHistory.json`.
*   **Headers:** The headers have been updated to match the "Golden Path" (Android mobile user agent).
*   **Compression Handling:** The code correctly checks for `Content-Encoding: gzip` and attempts decompression. It also handles `utf-8-sig` to strip BOM.
*   **Data Processing:** It parses the history JSON format.

### `web_app`
*   **Usage:** The web app calls `fetch_alerts()` which now hits the History endpoint.
*   **Implication:** This means the web app currently displays *history*, not necessarily *real-time* alerts with low latency (unless the history endpoint is also updated instantly, which it often is, but `Alerts.json` is the dedicated real-time feed).

## 3. Gaps & Recommendations

### Gaps
1.  **Real-time vs History:** The current implementation uses the **History** endpoint for everything. While this works, it might be heavier (larger payload) and slightly slower than the dedicated `Alerts.json` endpoint which is designed for high-frequency polling.
2.  **Polling Logic:** The web app just calls `fetch_alerts()` on demand (when the user refreshes or the frontend polls the backend). The HAR shows the official client polls every ~1 second.

### Technical Design for Improvements
1.  **Hybrid Approach:**
    *   Use `AlertsHistory.json` for the initial load to populate the view.
    *   Use `Alerts.json` for high-frequency polling (e.g., every 1-2 seconds) to detect new alerts instantly.
2.  **Frontend Polling:**
    *   The frontend (`app.js`) should implement the polling loop.
    *   The backend should expose a lightweight proxy to `Alerts.json` to avoid CORS issues if the frontend tried to hit Oref directly (though Oref might block direct browser requests from non-Oref domains).
3.  **Parser Update:**
    *   Update `OrefAlertParser` to support fetching from `Alerts.json` (handling the empty response case).

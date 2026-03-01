# API Reference

The Quiet Alert web server provides several REST endpoints for interacting with the alert data.

## Base URL
All API requests are relative to the server's base URL (default: `http://localhost:8080`).

---

## 1. Get Real-time Alerts
Returns a list of current active alerts in the system.

*   **Endpoint**: `/alerts`
*   **Method**: `GET`
*   **Response**: `Array<Alert>`

**Example Response**:
```json
[
  {
    "alertDate": "2024-01-01T12:00:00.000Z",
    "location": "Tel Aviv",
    "threat_type": "Missiles",
    "desc": "Red Alert"
  }
]
```

---

## 2. Get Approved Locations
Returns the list of cities and regions supported by the system for filtering.

*   **Endpoint**: `/api/approved-locations`
*   **Method**: `GET`
*   **Response**: `Object`

**Example Response**:
```json
{
  "locations": ["Tel Aviv", "Haifa", "Jerusalem"]
}
```

---

## 3. Get Combined Alerts for Location
Returns the most recent 50 alerts for a specific location, merged from real-time and historical sources.

*   **Endpoint**: `/api/alerts/all`
*   **Method**: `GET`
*   **Parameters**:
    *   `location` (required): The name of the city/region.
*   **Response**: `Object`

**Example Response**:
```json
{
  "alerts": [
    {
      "alertDate": "2024-01-01T12:00:00.000Z",
      "location": "Tel Aviv",
      "threat_type": "Missiles",
      "desc": "Red Alert"
    }
  ],
  "syncing": false
}
```

---

## 4. Force History Refresh
Tells the background poller to perform a fresh synchronization with the historical data source on the next cycle.

*   **Endpoint**: `/api/force-refresh`
*   **Method**: `POST`
*   **Response**: `Object`

**Example Response**:
```json
{
  "status": "success"
}
```

---

## Data Models

### Alert Object
| Field | Type | Description |
| :--- | :--- | :--- |
| `alertDate` | `string` | ISO 8601 formatted timestamp (Asia/Jerusalem). |
| `location` | `string \| Array<string>` | The location(s) affected by the alert. |
| `threat_type` | `string` | The type of threat (e.g., "Missiles", "Hostile Aircraft"). |
| `desc` | `string` | Additional description or instructions. |

# Quiet Alert 🚨

Quiet Alert is a real-time, high-visibility monitoring dashboard for Israeli security alerts. It provides instantaneous siren notifications, full historical logs, and a shelter-safety timer, optimized for both desktop and mobile use.

## Key Features

*   **Real-time Alerts**: Instant live polling (every 1-2 seconds) of the Home Front Command (Oref) API.
*   **Location-based Filtering**: Track alerts for specific cities or regions.
*   **Intelligent Shelter Timer**: Dynamic timer that helps users know when it's safe to leave the shelter (10-minute rule).
*   **Responsive Design**: A modern, dark-themed UI with high-visibility status blocks.
*   **Aurora Sync Animation**: Visual confirmation of active polling and manual refreshes.
*   **Exhaustive Test Suite**: Robust testing covering frontend logic, backend parsing, and end-to-end scenarios.

## Architecture

Quiet Alert is divided into two main components:

1.  **`oref_alert_parser`**: A local Python package that handles communication with alert providers (e.g., Oref). It uses a provider-based architecture, making it easy to add new data sources.
2.  **Web Server**: A Flask-based web application that manages background polling, data deduplication, and serves the real-time dashboard.

For more details, see [Architecture Documentation](docs/architecture.md).

## Installation

### Prerequisites

*   Python 3.10+
*   Node.js (for running E2E tests with Playwright)

### Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/tohar65/quiet_alert.git
    cd quiet_alert
    ```

2.  **Install the local parser package**:
    ```bash
    pip install -e ./oref_alert_parser
    ```

3.  **Install web application dependencies**:
    ```bash
    pip install -r web_app/requirements.txt
    ```

4.  **Install test dependencies (Optional)**:
    ```bash
    pip install pytest playwright pytest-playwright
    playwright install
    ```

## Usage

### Running the Web Server

Start the dashboard using the entry point script:

```bash
python run_app.py
```

The application will be available at `http://localhost:8080`.

### Using the CLI

The `oref_alert_parser` package provides a CLI for inspecting alerts directly:

```bash
# Get current alerts
oref-alert-parser
```

## Configuration

The application can be configured using environment variables. Default values are defined in [`web_app/config.py`](web_app/config.py).

| Variable | Description | Default |
| :--- | :--- | :--- |
| `OREF_HISTORY_URL` | URL for historical alerts API | `https://alerts-history.oref.org.il/...` |
| `OREF_REALTIME_URL` | URL for real-time alerts API | `https://www.oref.org.il/...` |
| `POLL_INTERVAL_REALTIME` | Polling frequency for live alerts (seconds) | `2.0` |
| `POLL_INTERVAL_HISTORY` | Polling frequency for history sync (seconds) | `10.0` |
| `PORT` | Port for the Flask server | `8080` |
| `DEBUG` | Enable Flask debug mode | `True` |

## Testing

Quiet Alert includes a comprehensive test suite.

### Run all tests:
```bash
pytest
```

### Run specific test suites:
```bash
# Core parser tests
pytest oref_alert_parser/tests

# Web server tests
pytest web_app/tests/test_web_server.py

# Frontend E2E tests
pytest web_app/tests/test_e2e_scenarios.py
```

## License

This project is licensed under the MIT License.

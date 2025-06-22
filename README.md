# Quiet Alert

Quiet Alert is a web application designed to fetch, parse, and display real-time alerts from a remote source. It provides a clean and quiet interface for monitoring alerts, with features for filtering by location and viewing historical data. The application includes both a web interface and a command-line tool.

## Features

-   **Real-time Alert Monitoring**: Fetches and displays alerts as they happen.
-   **Alert Categorization**: Automatically categorizes alerts based on their content.
-   **Location Filtering**: Allows users to view alerts for specific approved locations.
-   **Alert History**: Keeps a history of alerts for each location.
-   **Web Interface**: A user-friendly web UI for viewing and filtering alerts.
-   **Command-Line Interface**: A CLI tool for fetching and logging alerts.
-   **Comprehensive Test Suite**: Includes unit, integration, system, and end-to-end tests.

## Tech Stack

-   **Backend**: Python, FastAPI
-   **Frontend**: HTML, CSS, Vanilla JavaScript
-   **Testing**: Pytest, Selenium, `pytest-mock`

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd quiet_alert
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

### Web Server

To run the web application, use `uvicorn`:

```bash
uvicorn web_server:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

### Command-Line Interface (CLI)

The project also includes a command-line tool for fetching and logging alerts.

-   **Fetch all alerts:**
    ```bash
    python main.py
    ```

-   **Filter by location:**
    ```bash
    python main.py --locations "Location 1" "Location 2"
    ```

## Running Tests

The project has a comprehensive test suite. To run the tests, use `pytest`:

```bash
pytest
```

This will run all tests in the `tests/` directory, including unit, integration, system, and end-to-end tests.
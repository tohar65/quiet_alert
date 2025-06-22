# Quiet Alert

This project is composed of two main components:

1.  **`oref_alert_parser`**: A Python package for fetching and parsing real-time alerts.
2.  **`web_app`**: A Flask-based web application that uses the `oref_alert_parser` package to display alerts.

## oref_alert_parser

This is a self-contained Python package for fetching and parsing alerts from Israel's Home Front Command (Pikud Haoref) API.

### Installation

To install the package and its dependencies for development, run the following command from the `oref_alert_parser` directory:

```bash
pip install -e .
```

### Testing

To run the tests for the package, first install the test dependencies:

```bash
pip install -r requirements.txt
```

Then, run pytest from the `oref_alert_parser` directory:

```bash
pytest
```

## Web App

This is a Flask web application that consumes the `oref_alert_parser` package to provide a simple web interface for viewing alerts.

### Installation and Running

1.  Navigate to the `web_app` directory:
    ```bash
    cd web_app
    ```
2.  Install the `oref_alert_parser` package in editable mode from the parent directory and the web app's dependencies:
    ```bash
    pip install -e ../oref_alert_parser
    pip install -r requirements.txt
    ```
3.  Run the web server:
    ```bash
    python web_server.py
    ```
    The application will be available at `http://127.0.0.1:8080`.

### Testing

To run the tests for the web app, navigate to the `web_app` directory and run pytest:

```bash
cd web_app
pytest
```

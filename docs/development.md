# Development Guide

This guide provides information for developers who want to contribute to the Quiet Alert project.

## Development Environment Setup

### Prerequisites
*   Python 3.10 or higher.
*   Node.js (for Playwright tests).
*   A virtual environment is highly recommended.

### Step-by-Step Setup

1.  **Clone and create virtual environment**:
    ```bash
    git clone https://github.com/tohar65/quiet_alert.git
    cd quiet_alert
    python -m venv venv
    source venv/bin/activate  # Or venv\Scripts\activate on Windows
    ```

2.  **Install dependencies**:
    ```bash
    pip install -e ./oref_alert_parser
    pip install -r web_app/requirements.txt
    pip install pytest playwright pytest-playwright
    playwright install
    ```

## Coding Standards

### Python
*   **Type Hinting**: All core functions and classes must include PEP 484 type hints.
*   **Docstrings**: All public methods and classes must have Google-style docstrings.
    ```python
    def my_function(param1: int, param2: str) -> bool:
        """
        Brief description of the function.

        Args:
            param1: Description of param1.
            param2: Description of param2.

        Returns:
            Description of the return value.
        """
        return True
    ```
*   **Formatting**: Follow PEP 8 guidelines.

### JavaScript
*   Use vanilla JavaScript for the frontend.
*   Maintain clear and concise event-driven logic.

## Adding a New Alert Provider

Quiet Alert uses a provider-based architecture. To add a new data source:

1.  **Define a new class in `oref_alert_parser`**: Create a class that inherits from `AlertProvider`.
2.  **Implement required methods**:
    *   `fetch_latest_alerts()`: Fetch real-time alerts.
    *   `fetch_history()`: Fetch historical alerts.
3.  **Update the factory/instantiation**: Update `OrefAlertParser` or the entry points to use the new provider.

## Test-Driven Development (TDD)

We follow a strict TDD approach. All new features and bug fixes must be accompanied by relevant tests.

### Running the Test Suite
*   **Unit/Integration Tests**: `pytest`
*   **E2E Tests**: `pytest web_app/tests/test_e2e_scenarios.py`
*   **Coverage**: Run `pytest --cov=oref_alert_parser --cov=web_app` to check coverage.

## Project Structure
*   `oref_alert_parser/`: The core logic for fetching and parsing alerts.
*   `web_app/`: The Flask web server and frontend assets.
*   `docs/`: Technical documentation.
*   `plans/`: Architecture designs and refactoring strategies.
*   `scripts/`: Utility and verification scripts.

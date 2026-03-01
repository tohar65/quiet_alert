# Phase 3: Repository Refactor Strategy

The goal of this phase is to make the repository generic, clean, automated, and documented while preserving existing behavior and design.

## 1. Code Review & Analysis

### Current State
*   `oref_alert_parser`: Core package for fetching and parsing alerts.
*   `web_app`: Flask application for real-time visualization.
*   `scripts/`: Contains some verification and utility scripts.
*   `run_app.py`: Current entry point for the application.

### Identified Improvements
*   **Hardcoded Values**: URLs, headers, and polling intervals are hardcoded in `parser.py` and `web_server.py`.
*   **Provider Coupling**: The parser is tightly coupled with Oref API.
*   **Missing Metadata**: `setup.py` is missing dependencies, and `requirements.txt` is incomplete.
*   **Documentation**: Current documentation is minimal.
*   **One-off Scripts**: Many `verify_*.py` scripts exist (or were recently used) and need consolidation.

---

## 2. Generic & Clean

### Configuration Management
*   Implement a configuration system (e.g., using `python-dotenv` or a `config.py`).
*   Externalize:
    *   `OREF_HISTORY_URL`
    *   `OREF_REALTIME_URL`
    *   `USER_AGENT`
    *   `POLL_INTERVAL_REALTIME`
    *   `POLL_INTERVAL_HISTORY`
    *   `SERVER_PORT`

### Alert Provider Interface
*   Introduce an `AlertProvider` abstract base class to define the contract for fetching alerts.
*   Implement `OrefProvider` which inherits from `AlertProvider`.
*   This makes the system generic and ready for other sources (e.g., generic RSS, other national alert systems) in the future.

### Script Consolidation
*   Move all development/verification scripts to a dedicated `utils/` or keep in `scripts/` with clear naming.
*   Delete any redundant scripts that are covered by the main test suite.
*   Create a unified CLI tool for common tasks (e.g., `python manage.py test`, `python manage.py run`).

---

## 3. Best Practices & Documentation

### Best Practices
*   **Type Hinting**: Ensure all core functions and classes have PEP 484 type hints.
*   **Docstrings**: All public methods and classes should have Google-style docstrings.
*   **Dependency Management**: 
    *   Update `setup.py` with `install_requires`.
    *   Update `web_app/requirements.txt` to include all dependencies (including the `oref_alert_parser` package).

### Documentation Overhaul
*   **README.md**:
    *   Project vision and features.
    *   Quick start guide (installation and running).
    *   Architecture overview.
    *   License information.
*   **Technical Documentation (`docs/`)**:
    *   `architecture.md`: System design and data flow.
    *   `development.md`: Setting up dev environment, running tests, and contribution guidelines.
    *   `api.md`: Description of internal APIs and provider interface.

---

## 4. Automation

### Single Entry Point
*   Enhance `run_app.py` to support more modes (e.g., `--test`, `--dev`, `--cli`).
*   Or introduce a `Taskfile` or simple `run.py` to automate building, testing, and running.

---

## 5. Safety Net

*   All refactoring steps must be followed by a full test run of the Phase 2 test suite.
*   Refactoring will be done in small, incremental steps to ensure no regression.

---

## Implementation Roadmap

### Step 1: Cleanup & Metadata
1.  Remove redundant scripts.
2.  Update `setup.py` and `requirements.txt`.
3.  Implement basic configuration management.

### Step 2: Refactoring
1.  Define the `AlertProvider` interface.
2.  Refactor `OrefAlertParser` to use the provider.
3.  Inject dependencies in `web_server.py`.
4.  Apply type hints and docstrings.

### Step 3: Documentation
1.  Draft new `README.md`.
2.  Populate `docs/` directory.

### Step 4: Final Verification
1.  Run E2E tests.
2.  Verify CLI and Web functionality.

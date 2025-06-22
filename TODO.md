# Project TODO List

This file tracks the progress of the development tasks.

## Phase 1: Testing and Refactoring Existing Code
- [x] Create extensive unit tests for `alert_parser.py`.
- [x] Create extensive unit tests for `alert_types.py`.
- [x] Create system tests for the existing `main.py` functionality.
- [x] Run all tests and ensure they pass.
- [x] Fix any bugs found during testing.
- [x] Commit the initial tests and fixes.

## Phase 2: Location-Based Alert Filtering
- [x] Implement functionality to filter alerts by one or more locations.
- [x] Create unit tests for the new location-based filtering logic.
- [x] Create integration tests for the location-based filtering.
- [x] Run all tests and ensure they pass.
- [x] Commit the location-based filtering feature.

## Phase 3: Web Interface
- [x] Create a simple web server (e.g., using Flask or FastAPI).
- [x] Create an HTML page to display the alert status.
- [x] Add CSS for a modern and clear UI with appropriate colors for alerts.
- [x] Add JavaScript to fetch and display alert data every half second.
- [x] Implement an endpoint to get alerts for a specific location.
- [x] Commit the initial web interface.

## Phase 4: Web Interface Testing
- [x] Create system/E2E tests for the web interface.
- [x] Test setting a location and verifying the displayed alert status.
- [x] Ensure the UI updates correctly.
- [x] Run all tests and ensure they pass.
- [x] Commit the web interface tests.

## Phase 5: Finalization
- [x] Run all unit, integration, and system tests together.
- [x] Ensure the entire application works as expected.
- [x] Final commit of the project.
# Comprehensive Testing Strategy - Quiet Alert

This document outlines the strategy for achieving 100% test coverage for the Quiet Alert project.

## 1. Codebase Mapping

### Core Backend (`oref_alert_parser`)
- **`models.py`**: Data structures for `Alert`, `AlertStatus`, `ThreatType`.
- **`parser.py`**: 
    - `OrefAlertParser`: Core logic for parsing, categorizing, and deduplicating alerts.
    - `fetch_alerts()`: Historical data fetching with compression handling.
    - `fetch_realtime_alerts()`: Real-time data fetching.
    - Utility functions: `filter_alerts_by_location`, `save_alerts`, `display_alerts`.
- **`locations_updater.py`**: Script to update the approved locations list.
- **`approved_locations.py` / `locations.py`**: Static data for location validation.
- **`main.py`**: CLI entry point.

### Web Application (`web_app`)
- **`web_server.py`**: Flask server, background polling thread, API endpoints (`/alerts`, `/api/approved-locations`, `/api/force-refresh`, `/api/alerts/all`).
- **`static/app.js`**: Frontend logic, polling, state management (last location), timer logic, UI rendering.
- **`static/style.css`**: UI styling, including status-based themes and animations.
- **`templates/index.html`**: Base HTML structure.

---

## 2. Gap Analysis

### Existing Coverage
- Basic parsing of standard alerts (rocket, aircraft).
- Basic fetch mocking for historical and real-time endpoints.
- Basic Flask endpoint tests.
- Basic location filtering tests.

### Identified Gaps
- **Parser Edge Cases**: 
    - Alerts with Hebrew BOM but no GZIP.
    - Alerts with GZIP header but no GZIP content.
    - Unexpected `oref_category` values.
    - Multi-location alerts (lists vs strings).
    - Timezone edge cases (DST transitions).
- **Concurrency**: 
    - Race conditions in `web_server.py` cache access (though `Lock` is used, it needs stress testing).
    - Polling thread error recovery.
- **Frontend Logic**:
    - Timer transitions (especially "Safe to exit" at 10 minutes).
    - "Warning: Long delay" logic (>10 mins for upcoming alerts).
    - LocalStorage persistence and validation.
    - Error state UI (reconnecting indicator).
- **Integration**:
    - End-to-end flow from Oref API mock to Frontend display.
    - Data deduplication across history and real-time caches.

---

## 3. Testing Layers

### Level 1: Unit Tests (Python)
- **Models**: Validate `to_dict` and enum mappings.
- **Parser**: 
    - Test every known `oref_category`.
    - Test Hebrew string parsing for "ended" alerts.
    - Test deduplication with variations in seconds vs minutes.
    - Test `fetch` functions with malformed bytes, empty responses, and specific HTTP errors.
- **Locations**: Validate `update_approved_locations` logic with various log formats.

### Level 2: Unit/Component Tests (JavaScript)
- **Timer Logic**: Pure function tests for `formatTime` and `updateTimer` state transitions.
- **State Management**: Test `hasAlertsChanged` signature logic.
- **UI Components**: Mock `fetch` and verify DOM updates for different alert counts.

### Level 3: Integration Tests
- **API Integration**: Test `web_server.py` by mocking `parser.py` fetches.
- **Cache Sync**: Test the merger of history and real-time alerts in `all_alerts` endpoint.
- **Location Filter**: Ensure backend filtering matches frontend expectations (case sensitivity, whitespace).

### Level 4: System/E2E Tests
- **Playwright/Selenium**:
    - Scenario: User enters "פתח תקווה" -> Background syncs -> Alert appears -> Timer starts -> 10 mins pass -> "Safe to exit" appears.
    - Scenario: Server returns 500 -> Frontend shows "Reconnecting".
    - Scenario: Location not in approved list -> Button stays disabled.

---

## 4. Execution Plan (Phased)

### Phase 1: Foundation & High-Risk Core (Unit)
- [ ] Implement exhaustive parser tests (100+ cases including all categories).
- [ ] Implement robust `fetch` mocking with byte-level edge cases.
- [ ] Add tests for `locations_updater.py`.

### Phase 2: Backend API & Concurrency (Integration)
- [ ] Test `all_alerts` endpoint with overlapping data.
- [ ] Stress test `cache_lock` with concurrent API requests.
- [ ] Test `force-refresh` impact on background polling.

### Phase 3: Frontend Logic (JS Unit)
- [ ] Implement Jest/Mocha tests for `app.js` utility functions.
- [ ] Test timer state machine (Active -> 10m -> Safe).

### Phase 4: Full System (E2E)
- [ ] Playwright suite for happy path and error recovery.
- [ ] UI consistency checks (CSS class application).

---

## 5. Reassessment & Quality Control
- **Coverage Checkpoints**: Every 50 tests, run `pytest-cov` and ensure no regressions in coverage %.
- **Mutation Testing**: Use `mutmut` on the parser to ensure tests actually catch logic changes.
- **Strict Linting**: Enforce `mypy` and `flake8` to prevent "silent" bugs.

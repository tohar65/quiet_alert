# UI/UX Improvements Plan (Phase 4)

This document outlines the proposed UI/UX improvements for the `web_app`, focusing on clarity, professionalism, and feedback.

## 1. Refresh Dot & Live Sync Status
Currently, the "Live Sync" dot pulses subtly. We will improve it to provide clearer feedback on the "Last updated" status.

### Changes:
*   **Visual**: The dot will have a more pronounced "pulse" animation when a fetch is in progress.
*   **Status Text**: Add a small text next to or below the dot: "Live: <X>s ago".
*   **Tooltip**: Enhance the tooltip to show the exact last successful sync time.
*   **States**:
    *   **Active**: Green pulse, "Live: 2s ago".
    *   **Syncing**: Spinning/Expanding green ring, "Updating...".
    *   **Stale**: Orange dot if no update for > 10s, "Last update: 15s ago".
    *   **Error**: Red broken pulse, "Offline".

## 2. "Check Alerts" Button Enhancement
The button will be transformed into a more professional component with distinct states.

### Aurora Effect:
*   The aurora effect will be refined from a simple linear gradient sweep to a multi-layered, soft glowing effect using `box-shadow` and `::before`/`::after` pseudo-elements.
*   It will appear as a subtle background glow during idle/hover and become more energetic during the `loading` state.

### States:
*   **Idle**: Sleek blue gradient, subtle border-glow.
*   **Hover**: Slight lift (existing), intensified aurora glow.
*   **Loading**: Aurora glow accelerates, text changes to "Checking..." or shows a small spinner.
*   **Active (just clicked)**: "Flash" effect to indicate successful interaction.
*   **Disabled**: Muted gray, no glow.

## 3. General UI/UX Tweaks
*   **Transitions**:
    *   **Alert Entry**: Use a "Slide Down + Fade In" animation for new alerts.
    *   **Alert Exit**: Smooth fade out.
*   **Spacing & Typography**:
    *   Increase line-height for better readability in the history section.
    *   Slightly increase the font-weight of the location name in the main alert block.
    *   Adjust container padding for better mobile responsiveness.
*   **Timer**:
    *   The timer box should have a more integrated look, perhaps a subtle border matching the alert state (green for safe, red/orange for warning).

## 4. Implementation Plan

### CSS Changes (`web_app/static/style.css`):
1.  Define new keyframes for `aurora-flow` and `slide-in-up`.
2.  Update `#check-alerts-btn` with pseudo-elements for the aurora glow.
3.  Add `.sync-status-text` styles.
4.  Add `.alert-entry` animation class.

### JS Changes (`web_app/static/app.js`):
1.  Track `lastSuccessfulSync` timestamp.
2.  Implement a `setInterval` (1s) to update the "Live: X seconds ago" text.
3.  Add logic to handle the `syncing` state visually on the refresh dot.
4.  Apply the entry animation class when a new alert is rendered.

### Branch Strategy
All changes will be implemented in the branch: `feature/ui-ux-improvements`.

---
*Note: Core alert block colors (Green/Red/Yellow) will remain unchanged as per user preference.*

import pytest
from playwright.sync_api import Page, expect
from datetime import datetime

from alert_types import Alert, AlertStatus, ThreatType
from web_server import alert_manager, APPROVED_LOCATIONS


def test_alert_history_and_ui(page: Page, live_server, mocker):
    """
    End-to-end test for the UI, checking for active alerts and history.
    """
    # Define mock data
    active_alert = Alert(
        alertDate=datetime.now(),
        title="ירי רקטות וטילים",
        location="פתח תקווה",
        oref_category=1,
        status=AlertStatus.ACTIVE,
        threat_type=ThreatType.ROCKET,
    )
    inactive_alert = Alert(
        alertDate=datetime.now(),
        title="חדירת כלי טיס עוין",
        location="פתח תקווה",
        oref_category=1,
        status=AlertStatus.ENDED,
        threat_type=ThreatType.AIRCRAFT_INTRUSION,
    )
    all_alerts = [active_alert, inactive_alert]

    # Patch the alert manager methods and approved locations
    mocker.patch.object(alert_manager, 'get_active_alerts', return_value=[active_alert])
    mocker.patch.object(alert_manager, 'get_alert_history', return_value=all_alerts)
    mocker.patch('web_server.APPROVED_LOCATIONS', APPROVED_LOCATIONS + ["פתח תקווה"])

    # Navigate to the application
    page.on("console", lambda msg: print(f"PLAYWRIGHT CONSOLE: {msg.text()}"))
    page.goto("http://127.0.0.1:8000")

    # Enter a valid location and click the button
    page.locator("#location-input").fill("פתח תקווה")
    page.locator("#check-alerts-btn").click()

    # Wait for the main alert to be visible and verify its content
    main_alert = page.locator("#alerts-container .alert-item").first
    expect(main_alert).to_be_visible()
    expect(main_alert.locator(".alert-location")).to_have_text("פתח תקווה")
    expect(main_alert.locator(".alert-threat")).to_have_text("ירי רקטות וטילים")

    # Check for the new, larger font size
    font_size = main_alert.evaluate("element => window.getComputedStyle(element).fontSize")
    assert font_size == "40px"

    # Wait for the history to load and verify its structure
    history_container = page.locator("#history-container")
    expect(history_container).to_be_visible()

    # Verify the active history item
    active_item = history_container.locator(".history-item.active").first
    expect(active_item).to_be_visible()
    expect(active_item.locator(".history-threat")).to_have_text("ירי רקטות וטילים")
    expect(active_item.locator(".history-location")).to_have_text("פתח תקווה")
    border_color = active_item.evaluate("element => window.getComputedStyle(element).borderLeftColor")
    assert border_color == "rgb(255, 77, 77)"  # #ff4d4d

    # Verify the inactive history item
    inactive_item = history_container.locator(".history-item:not(.active)").first
    expect(inactive_item).to_be_visible()
    expect(inactive_item.locator(".history-threat")).to_have_text("חדירת כלי טיס עוין")
    expect(inactive_item.locator(".history-location")).to_have_text("פתח תקווה")
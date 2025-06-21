import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

@pytest.fixture
def driver():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    yield driver
    driver.quit()

def test_ui_alert_status_updates_correctly(driver, mocker):
    # Mock the API response
    mocker.patch(
        "alert_parser.fetch_alerts",
        return_value=json.dumps([{"data": "Red Alert", "title": "Test Alert", "location": "פתח תקווה"}])
    )

    # Navigate to the app
    driver.get("http://127.0.0.1:8000")

    # Interact with the UI
    location_input = driver.find_element(By.ID, "location-input")
    location_input.send_keys("פתח תקווה")
    set_location_button = driver.find_element(By.ID, "set-location-btn")
    set_location_button.click()

    # Wait for the status to update and assert
    WebDriverWait(driver, 10).until(
        lambda d: "Checking alerts" not in d.find_element(By.ID, "alert-status").text
    )
    status_div = driver.find_element(By.ID, "alert-status")
    
    # Assert that the "ALERT!" text is present
    assert "ALERT!" in status_div.text
    
    # Assert that the 'alert-active' class is present
    class_attribute = status_div.get_attribute("class")
    assert class_attribute is not None
    assert "alert-active" in class_attribute
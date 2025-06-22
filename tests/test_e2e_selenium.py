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

def test_ui_alert_status_updates_correctly(driver, live_server):
    # Navigate to the app
    driver.get("http://127.0.0.1:8000")

    # Interact with the UI
    location_input = driver.find_element(By.ID, "location-input")
    location_input.send_keys("פתח תקווה")
    set_location_button = driver.find_element(By.ID, "check-alerts-btn")
    set_location_button.click()

    # Wait for the alerts container to have an active alert
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#alerts-container .alert-item.active"))
    )

    # Find the active alert element
    alert_element = driver.find_element(By.CSS_SELECTOR, "#alerts-container .alert-item.active")

    # Assert that the location is correct
    location_element = alert_element.find_element(By.CLASS_NAME, "alert-location")
    assert "פתח תקווה" in location_element.text

    # Assert that the 'active' class is present
    class_attribute = alert_element.get_attribute("class")
    assert "active" in class_attribute
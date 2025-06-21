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
        "alert_parser.get_alerts_from_api",
        return_value=json.dumps([{"city": "Tel Aviv", "alerts": ["Red Alert"]}])
    )

    # Navigate to the app
    driver.get("http://127.0.0.1:8000")

    # Interact with the UI
    location_input = driver.find_element(By.ID, "location-input")
    location_input.send_keys("Tel Aviv")
    set_location_button = driver.find_element(By.ID, "set-location-button")
    set_location_button.click()

    # Wait for the status to update and assert
    status_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "status"))
    )
    
    # Assert that the "ALERT!" text is present
    assert "ALERT!" in status_div.text
    
    # Assert that the 'alert-active' class is present
    assert "alert-active" in status_div.get_attribute("class")
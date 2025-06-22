import pytest
import uvicorn
import multiprocessing
import time
import requests
from requests.exceptions import ConnectionError

def run_server():
    uvicorn.run("web_server:app", host="127.0.0.1", port=8000, log_level="info")

@pytest.fixture(scope="session")
def live_server():
    """
    Fixture that starts the a live server in a background process.
    """
    proc = multiprocessing.Process(target=run_server, daemon=True)
    proc.start()
    
    # Wait for the server to be ready
    for i in range(10):
        try:
            response = requests.get("http://127.0.0.1:8000/api/approved-locations")
            if response.status_code == 200:
                break
        except ConnectionError:
            time.sleep(0.5)
    else:
        proc.terminate()
        pytest.fail("Server did not start within 5 seconds.")
        
    yield
    proc.terminate()
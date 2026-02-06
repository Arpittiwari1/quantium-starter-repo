# tests/test_dash_ui_selenium.py
import importlib.util
import pathlib
import threading
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

ROOT = pathlib.Path(__file__).parent.parent

# Load app.py as a module regardless of PYTHONPATH
spec = importlib.util.spec_from_file_location("app", ROOT / "app.py")
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)


@pytest.fixture(scope="module")
def server():
    """Run the Dash app in a background thread for the duration of the tests."""
    thread = threading.Thread(
        target=app_module.app.run,
        kwargs={"debug": False, "use_reloader": False, "host": "127.0.0.1", "port": 8050},
        daemon=True,
    )
    thread.start()
    # Wait for the server to start accepting connections.
    # Poll the server URL until it responds or timeout.
    import requests

    start = time.time()
    timeout = 15.0
    url = "http://127.0.0.1:8050"
    while True:
        try:
            requests.get(url, timeout=1.0)
            break
        except Exception:
            if time.time() - start > timeout:
                raise RuntimeError("Dash server did not start within timeout")
            time.sleep(0.2)
    yield
    # daemon thread will exit when tests finish


@pytest.fixture
def driver():
    """Create a headless Chrome WebDriver using webdriver-manager."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Optional: reduce logging noise
    options.add_argument("--log-level=3")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


def wait_for_plotly_in_graph(driver, timeout=15):
    """Wait until Plotly has rendered inside the #sales-line container."""
    wait = WebDriverWait(driver, timeout)
    # Wait for the graph container to exist
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#sales-line")))
    # Then wait for Plotly's plot element inside it
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#sales-line .js-plotly-plot")))


def test_header_present(server, driver):
    driver.get("http://127.0.0.1:8050")
    wait = WebDriverWait(driver, 15)
    h1 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.title")))
    assert "Pink Morsel Sales Over Time" in h1.text


def test_visualisation_present(server, driver):
    driver.get("http://127.0.0.1:8050")
    # Wait for Plotly to render inside the graph container
    wait_for_plotly_in_graph(driver, timeout=20)
    graph = driver.find_element(By.CSS_SELECTOR, "#sales-line")
    assert graph is not None
    plotly = graph.find_elements(By.CSS_SELECTOR, ".js-plotly-plot")
    assert len(plotly) >= 1


def test_region_picker_present(server, driver):
    driver.get("http://127.0.0.1:8050")
    wait = WebDriverWait(driver, 15)
    radio = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#region-radio")))
    assert radio is not None
    labels = radio.find_elements(By.TAG_NAME, "label")
    texts = [lbl.text.strip().lower() for lbl in labels if lbl.text.strip()]
    for expected in ["north", "east", "south", "west", "all"]:
        assert any(expected in t for t in texts), f"Missing radio option: {expected}"

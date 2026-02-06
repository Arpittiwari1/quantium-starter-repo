# tests/test_dash_ui.py
import importlib.util
import pathlib
import time

import pytest

# Load app.py as a module regardless of PYTHONPATH
ROOT = pathlib.Path(__file__).parent.parent
spec = importlib.util.spec_from_file_location("app", ROOT / "app.py")
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)


def start_app(dash_duo):
    dash_duo.start_server(app_module.app)
    # wait briefly for initial render
    dash_duo.wait_for_element("h1.title", timeout=4)


def test_header_present(dash_duo):
    start_app(dash_duo)
    header = dash_duo.find_element("h1.title")
    assert header is not None
    assert "Pink Morsel Sales Over Time" in header.text


def test_visualisation_present(dash_duo):
    start_app(dash_duo)
    # Ensure the Graph container exists
    graph_container = dash_duo.find_element("#sales-line")
    assert graph_container is not None
    # Wait for Plotly to render inside the graph container
    # Plotly typically creates an element with class "js-plotly-plot"
    dash_duo.wait_for_element("#sales-line .js-plotly-plot", timeout=6)
    plotly_div = dash_duo.find_element("#sales-line .js-plotly-plot")
    assert plotly_div is not None


def test_region_picker_present(dash_duo):
    start_app(dash_duo)
    radio = dash_duo.find_element("#region-radio")
    assert radio is not None
    # radio items render labels; collect visible label texts
    labels = radio.find_elements_by_tag_name("label")
    texts = [lbl.text.strip().lower() for lbl in labels if lbl.text.strip()]
    for expected in ["north", "east", "south", "west", "all"]:
        assert any(expected in t for t in texts), f"Missing radio option: {expected}"

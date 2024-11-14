"""
Tests for the diagnostics models
"""

import json
import pytest
from multiprocessing import Process
from time import sleep

requests = pytest.importorskip("requests")

from ..diag import DiagnosticsData
from . import flowsheet


@pytest.fixture
def visualization_server(flowsheet):
    """Fixture to start the visualization server"""

    def run_server():
        flowsheet.visualize("sample_visualization", port=49999)

    server_process = Process(target=run_server)
    server_process.start()
    sleep(30)  # wait for the server to start

    yield
    # clean up server
    server_process.terminate()
    server_process.join()


# get diagnostics data from remote
def get_diagnostics_data(port, id):
    """Get diagnostics data from backend server
    Args:
        id: string, the flowsheet id usually it's the flowsheet name.
    Returns:
        JSON: diagnostics JSON file
    """
    url = f"http://localhost:{port}/diagnostics?id={id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


@pytest.mark.unit
def test_visualize_is_up(flowsheet):
    flowsheet.visualize("sample_visualization", port=49999)
    res = get_diagnostics_data(49999, "sample_visualization")
    assert res is not None


@pytest.mark.unit
def test_data(flowsheet):
    # start UI server
    flowsheet.visualize("sample_visualization", port=49999)

    # directly get diagnostics data
    diag_data = DiagnosticsData(flowsheet)

    # build diagnostics report base on data
    diag_data_config = diag_data.config
    diagnostics_toolbox_report = diag_data.diagnostics_toolbox_report
    build_diagnostics_report = {
        "config": diag_data_config,
        "diagnostics_toolbox_report": {
            "toolbox_jacobian_condition": diagnostics_toolbox_report.toolbox_jacobian_condition,
            "toolbox_model_statistics": diagnostics_toolbox_report.toolbox_model_statistics,
            "structural_report": diagnostics_toolbox_report.structural_report,
            "numerical_report": diagnostics_toolbox_report.numerical_report,
            "next_steps": diagnostics_toolbox_report.next_steps,
        },
    }
    # get diagnostics data from backend server
    remote_data = json.dumps(get_diagnostics_data(49999, "sample_visualization"))
    # compare the diagnostics data
    build_diagnostics_report = json.dumps(build_diagnostics_report)
    assert build_diagnostics_report == remote_data


# @pytest.mark.unit
def test_run_diagnostics_properties():
    remote_data = get_diagnostics_data(49999, "sample_visualization")
    assert "config" in remote_data
    assert "diagnostics_toolbox_report" in remote_data

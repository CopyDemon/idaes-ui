"""
Tests for the IDAES FV app, using FastAPI TestClient
"""
import pytest

from fastapi.testclient import TestClient
from ..app import FlowsheetApp
from ..fsvis import visualize
from idaes_ui.fv.tests.flowsheets import idaes_demo_flowsheet
import subprocess


# fixtures
@pytest.fixture(scope="module")  # build flowsheet only once
def fvapp():
    """Start the FastAPI app."""
    flowsheet = idaes_demo_flowsheet()
    app = visualize(
        flowsheet=flowsheet,
        name=flowsheet.name,
        port=8000,
        test=True,
        # clean up has to be True or if server in running server list it won't start a new fastapi and return None
        clean_up=True,
    )
    return app


@pytest.fixture
def client(fvapp):
    """FastAPI client for testing"""
    with TestClient(fvapp) as test_client:
        return test_client


@pytest.mark.unit
def test_diagnostics(client):
    response = client.get("/api/get_diagnostics")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_diagnostics(client):
    response = client.get("/api/get_diagnostics")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"config", "issues", "statistics"}


@pytest.mark.unit
def test_settings(client):
    # get app setting
    response = client.get("/api/get_app_setting")
    assert response.status_code == 200

    # update app setting
    data = {"save_time_interval": 2}
    response = client.put("/api/put_app_setting", json=data)
    res_json = response.json()
    assert res_json["save_time_interval"] == data["save_time_interval"]


@pytest.mark.unit
def test_get_settings(client):
    response = client.get("/api/get_app_setting")
    assert response.status_code == 200
    data = response.json()
    assert len(data.keys()) > 0


@pytest.mark.unit
def test_put_settings(client):
    response = client.get("/api/get_app_setting")
    data1 = response.json()
    data1["save_time_interval"] += 1
    client.put("/api/put_app_setting", json=data1)
    response = client.get("/api/get_app_setting")
    data2 = response.json()

    print(data1)
    print(data2)
    assert data1 == data2


@pytest.mark.unit
def test_fs(client):
    response = client.get("/api/get_fs?get_which=flowsheet")
    assert response.status_code == 200


@pytest.mark.unit
def test_get_fs(client):
    response = client.get("/api/get_fs?get_which=flowsheet")
    assert response.status_code == 200
    data = response.json()
    keys = set(data.keys())
    assert {"name", "model", "cells"}.issubset(keys)


@pytest.mark.unit
def test_put_fs(client):
    response = client.get("/api/get_fs?get_which=flowsheet")
    assert response.status_code == 200
    data1 = response.json()
    # modify position of 1st 'cell'
    cells = data1["cells"]
    cells[0]["position"]["x"] += 1
    # check that modification survived
    body = {"flowsheet_type": "jjs_fs", "flowsheet": data1}
    response = client.put("/api/put_fs", json=body)
    data2 = response.json()
    assert data1 == data2["flowsheet"]

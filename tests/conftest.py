from typing import List
import os

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.testclient import TestClient

from core import min_conections_count, test_facebook_user_id
from core import db_url, max_connections_count, test_facebook_user_token
from app import app
from routers.accounts import get_database


@pytest.fixture(scope="module")
def test_app() -> TestClient:
    client: TestClient = TestClient(app)
    yield client


@pytest.fixture(scope="module")
def test_authorization_header(test_app) -> str:
    response = test_app.post(url="/token", data={"username": test_facebook_user_id, "password": test_facebook_user_token})
    assert response.status_code == 200
    res_json = response.json()
    assert 'access_token' in res_json
    return "bearer " + res_json['access_token']


@pytest.fixture(scope="module")
def test_zones_list(test_app: TestClient, test_authorization_header) -> List:
    response = test_app.get(url="/zones/", headers={"Authorization": test_authorization_header})
    assert response.status_code == 200
    zones_dict = {"Pinar del Río":"Pinar del Río" ,
                      "Artemisa":"Artemisa",
                      "La Habana":"La Habana",
                      "Mayabeque": "Mayabeque",
                      "Matanzas":"Matanzas",
                      "Cienfuegos": "Cienfuegos",
                      "Villa Clara": "Villa Clara",
                      "Sancti Spíritus":"Sancti Spíritus",
                      "Ciego de Ávila": "Ciego de Ávila",
                      "Camagüey":"Camagüey",
                      "Las Tunas":"Las Tunas",
                      "Granma": "Granma",
                      "Holguín":"Holguín",
                      "Santiago de Cuba":"Santiago de Cuba",
                      "Guantánamo": "Guantánamo",
                      "Isla de la Juventud":"Isla de la Juventud"}
    count: int = 0
    res_json = response.json()
    zones_checked = {}
    for zone in res_json:
        count = count +1
        assert zone['name'] in zones_dict
        assert zone['name'] not in zones_checked
        zones_checked[zone['name']] = zone['name']
    assert count == 16
    return res_json


async def conn_db_test() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(str(db_url), maxPoolSize=max_connections_count, minPoolSize=min_conections_count)
    yield client
    client.close()


app.dependency_overrides[get_database] = conn_db_test


def root_path_tests():
    FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    return FILE_DIR





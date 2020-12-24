import pytest
from fastapi.testclient import TestClient

from src.app.core.config import test_facebook_user_id, test_facebook_user_token
from src.app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_login_for_access_token(test_app: TestClient):
    response = test_app.post(url="/token",data={"username": test_facebook_user_id, "password": test_facebook_user_token})
    assert response.status_code == 200


@pytest.mark.integration
def test_get_user_information(test_app: TestClient, test_authorization_header: str):
    response = test_app.post(url="/users/info", headers={"Authorization": test_authorization_header})
    assert response.status_code == 200
    assert response.json()["facebook_id"] == "10215843908959707"
    assert response.json()["name"] == "Yadisnel Gálvez Velázquez"
    assert response.json()["first_name"] == "Yadisnel"
    assert response.json()["last_name"] == "Gálvez Velázquez"




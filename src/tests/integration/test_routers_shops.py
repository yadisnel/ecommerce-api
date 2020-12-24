import os
import random
import uuid
from typing import List

import pytest
from fastapi.testclient import TestClient
from src.tests.conftest import root_path_tests
from src.app.models.user import UserDb

from src.app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_update_shop(test_app: TestClient, test_provinces_list: List, test_authorization_header: str):
    shop_name: str = "Shop name: " + str(uuid.UUID(bytes=os.urandom(16), version=4))
    province_index = random.randint(0, 15)
    lat: int = random.randint(-90, 90)
    long: int = random.randint(-180, 180)
    json_data = {
        "name": shop_name,
        "province_id": test_provinces_list[province_index]['id'],
        "location": {
            "lat": lat,
            "long": long
        },
    }
    response = test_app.post(url="/shops/update-shop", json=json_data, headers={"Authorization": test_authorization_header})
    assert response.status_code == 200
    json_response = response.json()
    assert response.status_code is not None
    assert "shop" in json_response
    assert "name" in json_response["shop"]
    assert json_response["shop"]["name"] == shop_name
    assert "province_id" in json_response["shop"]
    assert json_response["shop"]["province_id"] == test_provinces_list[province_index]['id']
    assert "province_name" in json_response["shop"]
    assert json_response["shop"]["province_name"] == test_provinces_list[province_index]['name']
    assert "location" in json_response["shop"]
    assert "coordinates" in json_response["shop"]["location"]
    assert len(json_response["shop"]["location"]["coordinates"]) == 2
    assert lat == json_response["shop"]["location"]["coordinates"][0]
    assert long == json_response["shop"]["location"]["coordinates"][1]


@pytest.mark.integration
def test_add_image_to_shop(test_app: TestClient, test_authorization_header: str):
    with open(os.path.join(root_path_tests(), "img/product.jpg"), 'rb') as file:
        response = test_app.post(url="/shops/remove-all-images-from-shop", headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        file_bytes = file.read()
        assert len(file_bytes) > 0
        files = {'file': ("product.jpg", file_bytes, "application/jpg")}
        response = test_app.post(url="/shops/add-image-to-shop", files=files, headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        response = test_app.post(url="/users/info", headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        user: UserDb = UserDb(**response.json())
        assert user is not None
        assert user.shop is not None
        assert user.shop.images is not None
        assert len(user.shop.images) == 1
        assert user.shop.images[0].id is not None
        assert user.shop.images[0].thumb_key is not None
        assert user.shop.images[0].original_key is not None


@pytest.mark.integration
def test_remove_image_from_shop(test_app: TestClient, test_authorization_header: str):
    with open(os.path.join(root_path_tests(), "img/product.jpg"), 'rb') as file:
        response = test_app.post(url="/shops/remove-all-images-from-shop", headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        file_bytes = file.read()
        assert len(file_bytes) > 0
        files = {'file': ("product.jpg", file_bytes, "application/jpg")}
        response = test_app.post(url="/shops/add-image-to-shop", files=files, headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        response = test_app.post(url="/users/info", headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        user: UserDb = UserDb(**response.json())
        assert user is not None
        assert user.shop is not None
        assert user.shop.images is not None
        assert len(user.shop.images) == 1
        json_data = {
            "image_id": user.shop.images[0].id
        }
        response = test_app.post(url="/shops/remove-image-from-shop", json=json_data,headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        response = test_app.post(url="/users/info", headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        user: UserDb = UserDb(**response.json())
        assert user is not None
        assert user.shop is not None
        assert user.shop.images is not None
        assert len(user.shop.images) == 0


@pytest.mark.integration
def test_clear_all_shop_images(test_app: TestClient, test_authorization_header):
    with open(os.path.join(root_path_tests(), "img/product.jpg"), 'rb') as file:
        response = test_app.post(url="/shops/remove-all-images-from-shop",headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        file_bytes = file.read()
        assert len(file_bytes) > 0
        files = {'file': ("product.jpg", file_bytes, "application/jpg")}
        response = test_app.post(url="/shops/add-image-to-shop", files=files,
                                 headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        response = test_app.post(url="/shops/add-image-to-shop", files=files,
                                 headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        response = test_app.post(url="/users/info", headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        user: UserDb = UserDb(**response.json())
        assert user is not None
        assert user.shop is not None
        assert user.shop.images is not None
        assert len(user.shop.images) == 2
        response = test_app.post(url="/shops/remove-all-images-from-shop", headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        response = test_app.post(url="/users/info", headers={"Authorization": test_authorization_header})
        assert response.status_code == 200
        user: UserDb = UserDb(**response.json())
        assert user is not None
        assert user.shop is not None
        assert user.shop.images is not None
        assert len(user.shop.images) ==0







import imghdr
import json
import os
import uuid
from datetime import datetime

import jwt
import requests
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from fastapi import File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from starlette.status import HTTP_412_PRECONDITION_FAILED

from src.app.core.config import admin_user, admin_pass
from src.app.core.config import image_thumb_resolution, image_big_resolution
from src.app.core.config import users_roles
from src.app.core.image import size, resize
from src.app.core.mongodb import AsyncIOMotorClient, get_database
from src.app.core.path import root_path
from src.app.crud.users import get_user_by_facebook_id_impl, add_user_impl, update_complete_user_by_id, \
    update_user_facebook_token_by_facebook_id_impl
from src.app.crud.users import update_user_token_by_user_id_impl
from src.app.models.shop import ShopIn
from src.app.models.token import Token
from src.app.models.user import UserDb, UserOut, UserIn
from src.app.core.config import url_users_images_on_s3_thumb, url_users_images_on_s3_big, bucket_config
from src.app.models.image import Image
from src.app.core.s3 import write_object_to_s3, delete_object_on_s3
from src.app.crud.users import update_user_avatar_impl
from typing import List


router = APIRouter()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "9420e933ba766ca93490f9a64629f024809855a4318847bbccbfb5aa0317eba6"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme),
                           conn: AsyncIOMotorClient = Depends(get_database)) -> UserDb:
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        facebook_id: str = payload.get("facebook_id")
        expires: float = payload.get("expires")
        if facebook_id is None:
            raise credentials_exception
        if expires < (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds():
            await update_user_facebook_token_by_facebook_id_impl(facebook_id=facebook_id, facebook_token=None)
            raise credentials_exception
        elif expires < ((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() - 864000):  # 10 days before expired:
            params_long_lived = {'grant_type': 'fb_exchange_token',
                                 'client_id': '841650690021376',
                                 'client_secret': 'ee44538b41f0e842e8569c7b78ec4fc1',
                                 'fb_exchange_token': payload['facebook_access_token']
                                 }
            response_long_lived = requests.get(url="https://graph.facebook.com/v6.0/oauth/access_token",
                                               params=params_long_lived)
            if response_long_lived.status_code != 200:
                await update_user_facebook_token_by_facebook_id_impl(facebook_id=facebook_id, facebook_token=None)
                raise credentials_exception
            json_data_long_lived = json.loads(response_long_lived.text)
            access_token = json_data_long_lived['access_token']
            token_type = json_data_long_lived['token_type']
            expires_in = json_data_long_lived['expires_in']
            params_profile = {'fields': 'name, first_name, last_name, picture, email',
                              'access_token': access_token
                              }
            response_profile = requests.get(url="https://graph.facebook.com/v6.0/me", params=params_profile)
            if response_profile.status_code != 200:
                HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Bad user or password",
                )
            user_db = await get_user_by_facebook_id_impl(facebook_id=facebook_id, conn=conn)
            json_data_profile = json.loads(response_profile.text)
            token_data = {'facebook_access_token': access_token,
                          'token_type': token_type,
                          'expires': (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() + expires_in,
                          'facebook_id': facebook_id,
                          'user_id': user_db.id
                          }
            encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
            user_db.token = encoded_jwt
            user_db.name = json_data_profile['name']
            user_db.first_name = json_data_profile['first_name']
            user_db.last_name = json_data_profile['last_name']
            utc_now = datetime.utcnow()
            user_db.modified_date = utc_now
            user_db.disabled = False
            async with await conn.start_session() as s:
                async with s.start_transaction():
                    return await update_complete_user_by_id(user_id=user_db.id, user_in=UserIn(**user_db.dict()),
                                                            conn=conn)
    except PyJWTError:
        raise credentials_exception
    user_db = await get_user_by_facebook_id_impl(facebook_id=facebook_id, conn=conn)
    if user_db is None:
        raise credentials_exception
    return user_db


async def get_current_active_user(current_user: UserDb = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(
            status_code=HTTP_412_PRECONDITION_FAILED,
            detail="User status is disabled",
        )
    return current_user


async def get_current_active_admin_user(current_user: UserDb = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(
            status_code=HTTP_412_PRECONDITION_FAILED,
            detail="User status is disabled",
        )
    if current_user.role != users_roles['admin']:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User must be admin.",
        )
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 conn: AsyncIOMotorClient = Depends(get_database)):
    params_long_lived = {'grant_type': 'fb_exchange_token',
                         'client_id': '841650690021376',
                         'client_secret': 'ee44538b41f0e842e8569c7b78ec4fc1',
                         'fb_exchange_token': form_data.password
                         }
    response_long_lived = requests.get(url="https://graph.facebook.com/v6.0/oauth/access_token",
                                       params=params_long_lived)
    if response_long_lived.status_code != 200:
        HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Bad user or password",
        )
    json_data_long_lived = json.loads(response_long_lived.text)
    access_token = json_data_long_lived['access_token']
    token_type = json_data_long_lived['token_type']
    expires_in = json_data_long_lived['expires_in']
    params_profile = {'fields': 'name, first_name, last_name, picture, email',
                      'access_token': access_token
                      }
    response_profile = requests.get(url="https://graph.facebook.com/v6.0/me", params=params_profile)
    if response_profile.status_code != 200:
        HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Bad user or password",
        )
    async with await conn.start_session() as s:
        async with s.start_transaction():
            user_db = await get_user_by_facebook_id_impl(facebook_id=form_data.username, conn=conn)
            json_data_profile = json.loads(response_profile.text)
            user_in: UserIn = UserIn()
            user_in.facebook_id = form_data.username
            user_in.token = None
            user_in.name = json_data_profile['name']
            user_in.first_name = json_data_profile['first_name']
            user_in.last_name = json_data_profile['last_name']
            user_in.picture = None
            user_in.role = users_roles['user']
            utc_now = datetime.utcnow()
            user_in.create_date = utc_now
            user_in.modified_date = utc_now
            shop: ShopIn = ShopIn()
            shop.name = "Tienda de " + user_in.name
            shop.images = []
            shop.location = None
            shop.province_id = None
            shop.province_name = None
            user_in.shop = shop
            user_in.disabled = False
            if user_db is None:
                user_db = await add_user_impl(user_in=user_in, conn=conn)
            token_data = {'facebook_access_token': access_token,
                          'token_type': token_type,
                          'expires': (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() + expires_in,
                          'facebook_id': form_data.username,
                          'user_id': user_db.id
                          }
            encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
            user_db.token = encoded_jwt
            user_db.modified_date = datetime.utcnow()
            await update_user_token_by_user_id_impl(user_id=user_db.id, token=encoded_jwt, conn=conn)
    return {"access_token": encoded_jwt, "token_type": token_type}


@router.post("/users/info", response_model=UserOut)
async def get_user_information(current_user: UserDb = Depends(get_current_active_user)):
    user_out: UserOut = UserOut(**current_user.dict())
    return user_out


@router.post("/users/update-avatar", response_model=UserOut)
async def update_user_avatar(current_user: UserDb = Depends(get_current_active_user),
                               file: UploadFile = File(...),
                               conn: AsyncIOMotorClient = Depends(get_database)):
    filename_original = str(uuid.UUID(bytes=os.urandom(16), version=4)) + "_original_.png"
    filename_big = str(uuid.UUID(bytes=os.urandom(16), version=4)) + "_big_.png"
    filename_thumb = str(uuid.UUID(bytes=os.urandom(16), version=4)) + "_thumb_.png"
    file_path = os.path.join(root_path(), 'tmp', filename_original)
    file_bytes_original = await file.read()
    file_bytes_big = resize(file_bytes_original, image_big_resolution)
    file_bytes_thumb = resize(file_bytes_original, image_thumb_resolution)
    with open(file_path, 'wb') as f:
        f.write(file_bytes_original)
    isvalid = imghdr.what(os.path.join(file_path)) is not None
    os.remove(file_path)
    if not isvalid:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="File must be image type.",
        )
    key_big = url_users_images_on_s3_big + filename_big
    key_thumb = url_users_images_on_s3_thumb + filename_thumb
    write_object_to_s3(file_bytes=file_bytes_big, bucket=bucket_config.name(),
                       key=key_big, region_name=bucket_config.region())
    write_object_to_s3(file_bytes=file_bytes_thumb, bucket=bucket_config.name(),
                       key=key_thumb, region_name=bucket_config.region())
    original_height, original_width = size(file_bytes_big)
    original_size = len(file_bytes_big)
    thumb_height, thumb_width = size(file_bytes_thumb)
    thumb_size = len(file_bytes_thumb)
    image_in: Image = Image()
    image_in.id = str(uuid.UUID(bytes=os.urandom(16), version=4))
    image_in.original_key = key_big
    image_in.original_width = original_width
    image_in.original_height = original_height
    image_in.original_size = original_size
    image_in.thumb_key = key_thumb
    image_in.thumb_width = thumb_width
    image_in.thumb_height = thumb_height
    image_in.thumb_size = thumb_size
    if current_user.picture is not None:
        delete_object_on_s3(bucket=bucket_config.name(),key=current_user.picture.thumb_key, region_name=bucket_config.region())
        delete_object_on_s3(bucket=bucket_config.name(),key=current_user.picture.original_key, region_name=bucket_config.region())
    user_db: UserDb = await update_user_avatar_impl(user_id=current_user.id, image_in=image_in, conn=conn)
    user_out: UserOut = UserOut(**user_db.dict())
    return user_out


@router.post("/users/mqtt/auth-user")
async def emqx_auth_http_user(request: Request, conn: AsyncIOMotorClient = Depends(get_database)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = await request.form()
        if 'username' not in payload or 'password' not in payload:
            raise credentials_exception
        username: str = payload['username']
        password: str = payload['password']
        if username == admin_user and password == admin_pass:
            return {"success": True}
        if username != password:
            raise credentials_exception
        payload = jwt.decode(username, SECRET_KEY, algorithms=[ALGORITHM])
        facebook_id: str = payload.get("facebook_id")
        expires: float = payload.get("expires")
        user_id: str = payload.get("user_id")
        if facebook_id is None:
            raise credentials_exception
        if user_id is None:
            raise credentials_exception
        if expires < (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds():
            raise credentials_exception
        user_db = await get_user_by_facebook_id_impl(facebook_id=facebook_id, conn=conn)
        if user_db is None or user_db.disabled:
            raise credentials_exception
        return {"success": True}
    except PyJWTError:
        raise credentials_exception


@router.post("/users/mqtt/auth-admin")
async def emqx_auth_http_admin(request: Request, conn: AsyncIOMotorClient = Depends(get_database)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = await request.form()
        if 'username' not in payload or 'password' not in payload:
            raise credentials_exception
        username: str = payload['username']
        password: str = payload['password']
        if username == admin_user and password == admin_pass:
            return {"success": True}
        if username != password:
            raise credentials_exception
        payload = jwt.decode(username, SECRET_KEY, algorithms=[ALGORITHM])
        facebook_id: str = payload.get("facebook_id")
        expires: float = payload.get("expires")
        user_id: str = payload.get("user_id")
        if facebook_id is None:
            raise credentials_exception
        if user_id is None:
            raise credentials_exception
        if expires < (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds():
            raise credentials_exception
        user_db = await get_user_by_facebook_id_impl(facebook_id=facebook_id, conn=conn)
        if user_db is None or user_db.disabled:
            raise credentials_exception
        if user_db.role != users_roles['admin']:
            raise credentials_exception
        return {"success": True}
    except PyJWTError:
        raise credentials_exception


@router.post("/users/mqtt/auth-acl")
async def emqx_auth_http_acl(request: Request, conn: AsyncIOMotorClient = Depends(get_database)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = await request.form()
        if 'username' not in payload or 'access' not in payload or 'ipaddr' not in payload or 'topic' not in payload:
            raise credentials_exception
        username: str = payload['username']
        access: str = payload['access']
        ipaddr: str = payload['ipaddr']
        topic: str = payload['topic']
        if username == admin_user:
            return {"success": True}
        if access != "1":
            raise credentials_exception
        payload = jwt.decode(username, SECRET_KEY, algorithms=[ALGORITHM])
        facebook_id: str = payload.get("facebook_id")
        expires: float = payload.get("expires")
        user_id: str = payload.get("user_id")
        if facebook_id is None:
            raise credentials_exception
        if user_id is None:
            raise credentials_exception
        if expires < (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds():
            raise credentials_exception
        if topic != "users/" + user_id and  topic != "users/" + user_id and topic != "users/all":
            raise credentials_exception
        if topic == "users/" + user_id:
            if access != "2":
                raise credentials_exception
        if topic == "users/" + user_id:
            if access != "1":
                raise credentials_exception
        if topic == "users/all":
            if access != "1":
                raise credentials_exception
        user_db = await get_user_by_facebook_id_impl(facebook_id=facebook_id, conn=conn)
        if user_db is None or user_db.disabled:
            raise credentials_exception
        return {"success": True}
    except PyJWTError:
        raise credentials_exception


@router.post("/test/")
async def create_upload_files(request: Request):
    payload = await request.body()
    print(payload)
    return {"success": True}
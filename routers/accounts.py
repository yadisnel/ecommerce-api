import imghdr
import os
import uuid
import jwt
from fastapi import APIRouter
from fastapi import Body

from fastapi import Depends, HTTPException
from fastapi import File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from starlette.status import HTTP_412_PRECONDITION_FAILED, HTTP_200_OK, HTTP_406_NOT_ACCEPTABLE

from core.cloud_front import get_signed_url
from core.config import admin_user, admin_pass
from core.config import image_thumb_resolution, image_big_resolution
from core.config import users_roles
from core.image import size, resize
from core.ses import send_registry_email_to_customer
from core.mongodb import AsyncIOMotorClient, get_database
from core.path import root_path
from core.security import is_strong_password, verify_password
from crud.accounts import get_account_by_facebook_id_impl, add_account_impl, \
 get_standard_account_by_email_impl, update_account_avatar_impl
from crud.pending_accounts import add_standard_pending_account_with_email, get_pending_account_by_email_impl, \
    delete_standard_pending_account_by_email
from models.tokens import Token, TokenData
from models.accounts import AccountDb, AccountOut, AccountIn, StandardAccountInfo
from core.config import url_users_images_on_s3_thumb, url_users_images_on_s3_big, bucket_config
from models.images import ImageDb
from core.s3 import write_object_to_s3, delete_object_on_s3
from erequests.accounts import RequestRegisterAccountWithEmail, RequestConfirmRegisterAccountWithEmail
from datetime import datetime, timedelta

router = APIRouter()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "9420e933ba766ca93490f9a64629f024809855a4318847bbccbfb5aa0317eba6"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # 30 days


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=43200)  # 30 days
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme),
                           conn: AsyncIOMotorClient = Depends(get_database)) -> AccountDb:
    # credentials_exception = HTTPException(
    #     status_code=HTTP_401_UNAUTHORIZED,
    #     detail="Could not validate credentials",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    # try:
    #     payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    #     facebook_id: str = payload.get("facebook_id")
    #     expires: float = payload.get("expires")
    #     if facebook_id is None:
    #         raise credentials_exception
    #     if expires < (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds():
    #         await update_account_facebook_token_by_facebook_id_impl(facebook_id=facebook_id, facebook_token=None,
    #                                                                 conn=conn)
    #         raise credentials_exception
    #     elif expires < ((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() - 864000):  # 10 days before expired:
    #         params_long_lived = {'grant_type': 'fb_exchange_token',
    #                              'client_id': '841650690021376',
    #                              'client_secret': 'ee44538b41f0e842e8569c7b78ec4fc1',
    #                              'fb_exchange_token': payload['facebook_access_token']
    #                              }
    #         response_long_lived = requests.get(url="https://graph.facebook.com/v6.0/oauth/access_token",
    #                                            params=params_long_lived)
    #         if response_long_lived.status_code != 200:
    #             await update_account_facebook_token_by_facebook_id_impl(facebook_id=facebook_id, facebook_token=None,
    #                                                                     conn=conn)
    #             raise credentials_exception
    #         json_data_long_lived = json.loads(response_long_lived.text)
    #         access_token = json_data_long_lived['access_token']
    #         token_type = json_data_long_lived['token_type']
    #         expires_in = json_data_long_lived['expires_in']
    #         params_profile = {'fields': 'name, first_name, last_name, picture, email',
    #                           'access_token': access_token
    #                           }
    #         response_profile = requests.get(url="https://graph.facebook.com/v6.0/me", params=params_profile)
    #         if response_profile.status_code != 200:
    #             HTTPException(
    #                 status_code=HTTP_401_UNAUTHORIZED,
    #                 detail="Bad user or password",
    #             )
    #         user_db = await get_account_by_facebook_id_impl(facebook_id=facebook_id, conn=conn)
    #         json_data_profile = json.loads(response_profile.text)
    #         token_data = {'facebook_access_token': access_token,
    #                       'token_type': token_type,
    #                       'expires': (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() + expires_in,
    #                       'facebook_id': facebook_id,
    #                       'user_id': user_db.id
    #                       }
    #         encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    #         user_db.token = encoded_jwt
    #         user_db.name = json_data_profile['name']
    #         user_db.first_name = json_data_profile['first_name']
    #         user_db.last_name = json_data_profile['last_name']
    #         utc_now = datetime.utcnow()
    #         user_db.modified_date = utc_now
    #         user_db.disabled = False
    #         async with await conn.start_session() as s:
    #             async with s.start_transaction():
    #                 return await update_complete_account_by_id(user_id=user_db.id, user_in=AccountIn(**user_db.dict()),
    #                                                            conn=conn)
    # except PyJWTError:
    #     raise credentials_exception
    # user_db = await get_account_by_facebook_id_impl(facebook_id=facebook_id, conn=conn)
    # if user_db is None:
    #     raise credentials_exception
    # return user_db
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user_in_db = await get_standard_account_by_email_impl(conn=conn, email=token_data.username)
    if user_in_db is None:
        raise credentials_exception
    return user_in_db


async def get_current_active_user(current_user: AccountDb = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(
            status_code=HTTP_412_PRECONDITION_FAILED,
            detail="User status is disabled",
        )
    return current_user


async def get_current_active_admin_user(current_user: AccountDb = Depends(get_current_user)):
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
    # params_long_lived = {'grant_type': 'fb_exchange_token',
    #                      'client_id': '841650690021376',
    #                      'client_secret': 'ee44538b41f0e842e8569c7b78ec4fc1',
    #                      'fb_exchange_token': form_data.password
    #                      }
    # response_long_lived = requests.get(url="https://graph.facebook.com/v6.0/oauth/access_token",
    #                                    params=params_long_lived)
    # if response_long_lived.status_code != 200:
    #     raise HTTPException(
    #         status_code=HTTP_401_UNAUTHORIZED,
    #         detail="Bad user or password",
    #     )
    # json_data_long_lived = json.loads(response_long_lived.text)
    # access_token = json_data_long_lived['access_token']
    # token_type = json_data_long_lived['token_type']
    # expires_in = json_data_long_lived['expires_in']
    # params_profile = {'fields': 'name, first_name, last_name, picture, email',
    #                   'access_token': access_token
    #                   }
    # response_profile = requests.get(url="https://graph.facebook.com/v6.0/me", params=params_profile)
    # if response_profile.status_code != 200:
    #     raise HTTPException(
    #         status_code=HTTP_401_UNAUTHORIZED,
    #         detail="Bad user or password",
    #     )
    # async with await conn.start_session() as s:
    #     async with s.start_transaction():
    #         user_db = await get_account_by_facebook_id_impl(facebook_id=form_data.username, conn=conn)
    #         json_data_profile = json.loads(response_profile.text)
    #         user_in: AccountIn = AccountIn()
    #         user_in.facebook_id = form_data.username
    #         user_in.token = None
    #         user_in.name = json_data_profile['name']
    #         user_in.first_name = json_data_profile['first_name']
    #         user_in.last_name = json_data_profile['last_name']
    #         user_in.picture = None
    #         user_in.role = users_roles['user']
    #         utc_now = datetime.utcnow()
    #         user_in.create_date = utc_now
    #         user_in.modified_date = utc_now
    #         shop: ShopIn = ShopIn()
    #         shop.name = "Tienda de " + user_in.name
    #         shop.images = []
    #         shop.location = None
    #         shop.zone_id = None
    #         shop.zone_name = None
    #         user_in.shop = shop
    #         user_in.disabled = False
    #         if user_db is None:
    #             user_db = await add_account_impl(account_in=user_in, conn=conn)
    #         token_data = {'facebook_access_token': access_token,
    #                       'token_type': token_type,
    #                       'expires': (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() + expires_in,
    #                       'facebook_id': form_data.username,
    #                       'user_id': user_db.id
    #                       }
    #         encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    #         user_db.token = encoded_jwt
    #         user_db.modified_date = datetime.utcnow()
    #         await update_account_facebook_token_by_facebook_id_impl(facebook_id=user_db.facebook_account_info.id, facebook_token=encoded_jwt, conn=conn)
    # return {"access_token": encoded_jwt, "token_type": token_type}
    # TODO Test, remove it in production!!!!
    if form_data.password == "Hypertest123admin":
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": form_data.username},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    user_in_db = await get_standard_account_by_email_impl(conn=conn, email=form_data.username)
    if not user_in_db or not verify_password(form_data.password, user_in_db.standard_account_info.hashed_password):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Incorrect email or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in_db.standard_account_info.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/accounts/info", response_model=AccountOut)
async def get_user_information(current_user: AccountDb = Depends(get_current_active_user)):
    user_out: AccountOut = AccountOut(**current_user.dict())
    return user_out


@router.post("/accounts/register-with-email", status_code=HTTP_200_OK)
async def register_with_email(e_request: RequestRegisterAccountWithEmail = Body(..., title="body request"),
                              conn: AsyncIOMotorClient = Depends(get_database)):
    async with await conn.start_session() as s:
        async with s.start_transaction():
            account_in_db = await get_standard_account_by_email_impl(conn=conn, email=e_request.email)
            if account_in_db is not None:
                raise HTTPException(
                    status_code=HTTP_412_PRECONDITION_FAILED,
                    detail="User with this email already exists",
                )
            if e_request.locale != "es_ES" and \
                    e_request.locale != "en_US" \
                    and e_request.locale != "sr_Latn"\
                    and e_request.locale != "sr_Latn"\
                    and e_request.locale != "fr_CA":
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid locale. Only 'es_ES',  'en_US', 'sr_Latn' and 'fr_CA' are supported.",
                )
            if e_request.country_iso_code != "CU" \
                    and e_request.country_iso_code != "US" \
                    and e_request.country_iso_code != "SR" \
                    and e_request.country_iso_code != "UY"\
                    and e_request.country_iso_code != "ES"\
                    and e_request.country_iso_code != "CA":
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid country_iso_code. Only 'CU','US', 'UY', 'SR','ES', and 'CA' are supported.",
                )
            if not is_strong_password(password=e_request.password):
                raise HTTPException(
                    status_code=HTTP_406_NOT_ACCEPTABLE,
                    detail="Invalid password. Minimum 8 characters, at least one number, at least one Uppercase letter, at least one lowercase letter.",
                )
            pending_account_in_db = await add_standard_pending_account_with_email(conn=conn,
                                                                                  e_request=e_request)
            await send_registry_email_to_customer(email=pending_account_in_db.email,
                                                  security_code=pending_account_in_db.security_code,
                                                  locale=e_request.locale)
            return {"success": True}


@router.post("/accounts/confirm-register-with-email", status_code=HTTP_200_OK)
async def confirm_register_with_email(e_request: RequestConfirmRegisterAccountWithEmail = Body(..., title="body request"),
                                      conn: AsyncIOMotorClient = Depends(get_database)) -> AccountOut:
    async with await conn.start_session() as s:
        async with s.start_transaction():
            account_pending_in_db = await get_pending_account_by_email_impl(conn=conn, email=e_request.email)
            if not account_pending_in_db or not account_pending_in_db.security_code == e_request.security_code:
                raise HTTPException(
                    status_code=HTTP_412_PRECONDITION_FAILED,
                    detail="There is not pending user with this email.",
                )
            account_db = await get_standard_account_by_email_impl(conn=conn, email=e_request.email)
            if account_db:
                raise HTTPException(
                    status_code=HTTP_406_NOT_ACCEPTABLE,
                    detail="User already exists.",
                )
            now = datetime.now()
            date = datetime.timestamp(now)
            date = date * 1000
            account_in = AccountIn()
            account_in.name = None
            account_in.first_name = None
            account_in.last_name = None
            account_in.avatar = None
            account_in.role = users_roles["user"]
            account_in.create_at = int(date)
            account_in.modified_at = int(date)
            account_in.disabled = False
            standard_account_info: StandardAccountInfo = StandardAccountInfo()
            standard_account_info.hashed_password = account_pending_in_db.hashed_password
            standard_account_info.email = account_pending_in_db.email
            account_in.standard_account_info = standard_account_info
            account_in.facebook_account_info = None
            account_in.is_standard_account = True
            account_in.is_facebook_account = False
            account_in.country_iso_code = account_pending_in_db.country_iso_code
            account_db = await add_account_impl(conn=conn, account_in=account_in)
            await delete_standard_pending_account_by_email(conn=conn, email=e_request.email)
            return AccountOut(**account_db.dict())


@router.put("/accounts/avatar", response_model=AccountOut)
async def update_account_avatar(current_account: AccountDb = Depends(get_current_active_user),
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
    image_in: ImageDb = ImageDb()
    image_in.id = str(uuid.UUID(bytes=os.urandom(16), version=4))
    image_in.original_key = key_big
    image_in.original_width = original_width
    image_in.original_height = original_height
    image_in.original_size = original_size
    image_in.thumb_key = key_thumb
    image_in.thumb_width = thumb_width
    image_in.thumb_height = thumb_height
    image_in.thumb_size = thumb_size
    image_in.original_url = get_signed_url(s3_key=key_big)
    image_in.thumb_url = get_signed_url(s3_key=key_thumb)
    if current_account.avatar is not None:
        delete_object_on_s3(bucket=bucket_config.name(), key=current_account.avatar.thumb_key,
                            region_name=bucket_config.region())
        delete_object_on_s3(bucket=bucket_config.name(), key=current_account.avatar.original_key,
                            region_name=bucket_config.region())
    user_db: AccountDb = await update_account_avatar_impl(account_id=current_account.id, image_in=image_in, conn=conn)
    user_out: AccountOut = AccountOut(**user_db.dict())
    return user_out


@router.post("/accounts/real-time/auth-user")
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
        user_db = await get_account_by_facebook_id_impl(facebook_id=facebook_id, conn=conn)
        if user_db is None or user_db.disabled:
            raise credentials_exception
        return {"success": True}
    except PyJWTError:
        raise credentials_exception


@router.post("/accounts/real-time/auth-admin")
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
        user_db = await get_account_by_facebook_id_impl(facebook_id=facebook_id, conn=conn)
        if user_db is None or user_db.disabled:
            raise credentials_exception
        if user_db.role != users_roles['admin']:
            raise credentials_exception
        return {"success": True}
    except PyJWTError:
        raise credentials_exception


@router.post("/accounts/real-time/auth-acl")
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
        if topic != "users/" + user_id and topic != "users/" + user_id and topic != "users/all":
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
        user_db = await get_account_by_facebook_id_impl(facebook_id=facebook_id, conn=conn)
        if user_db is None or user_db.disabled:
            raise credentials_exception
        return {"success": True}
    except PyJWTError:
        raise credentials_exception

from datetime import datetime

from models.rwmodels import RwModel
from models.images import Image


class StandardAccountInfo(RwModel):
    email: str = None
    hashed_password: str = None


class FacebookAccountInfo(RwModel):
    id: str = None
    token: bytes = None


class AccountIn(RwModel):
    name: str = None
    first_name: str = None
    last_name: str = None
    picture: Image = None
    role: str = None
    create_at: datetime = None
    modified_at: datetime = None
    disabled: bool = None
    standard_account_info: StandardAccountInfo = None
    facebook_account_info: FacebookAccountInfo = None
    is_standard_account:bool = None
    is_facebook_account: bool = None


class AccountOut(RwModel):
    id: str = None
    name: str = None
    first_name: str = None
    last_name: str = None
    picture: Image = None
    role:str = None
    create_at: datetime = None
    modified_at: datetime = None
    disabled: bool = None


class AccountDb(RwModel):
    id: str = None
    name: str = None
    first_name: str = None
    last_name: str = None
    picture: Image = None
    role: str = None
    create_at: datetime = None
    modified_at: datetime = None
    disabled: bool = None
    standard_account_info: StandardAccountInfo = None
    facebook_account_info: FacebookAccountInfo = None
    is_standard_account:bool = None
    is_facebook_account: bool = None


























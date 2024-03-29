from datetime import datetime
from typing import List

from models.rwmodels import RwModel
from models.images import ImageDb
from models.shops import ShopOut


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
    avatar: ImageDb = None
    role: str = None
    create_at: datetime = None
    modified_at: datetime = None
    disabled: bool = None
    standard_account_info: StandardAccountInfo = None
    facebook_account_info: FacebookAccountInfo = None
    is_standard_account:bool = None
    is_facebook_account: bool = None
    country_iso_code: str = None


class AccountOut(RwModel):
    id: str = None
    name: str = None
    first_name: str = None
    last_name: str = None
    avatar: ImageDb = None
    role:str = None
    create_at: datetime = None
    modified_at: datetime = None
    disabled: bool = None
    country_iso_code: str = None
    shops: List[ShopOut] = None


class AccountDb(RwModel):
    id: str = None
    name: str = None
    first_name: str = None
    last_name: str = None
    avatar: ImageDb = None
    role: str = None
    create_at: datetime = None
    modified_at: datetime = None
    disabled: bool = None
    standard_account_info: StandardAccountInfo = None
    facebook_account_info: FacebookAccountInfo = None
    is_standard_account:bool = None
    is_facebook_account: bool = None
    country_iso_code: str = None



























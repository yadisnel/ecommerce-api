from datetime import datetime

from models.rwmodels import RwModel
from models.shops import ShopIn, ShopOut, ShopDb
from models.images import Image


class AccountOut(RwModel):
    id: str = None
    facebook_id: str = None
    name: str = None
    first_name: str = None
    last_name: str = None
    picture: Image = None
    role:str = None
    create_date: datetime = None
    modified_date: datetime = None
    disabled: bool = None
    shop: ShopOut = None


class AccountIn(RwModel):
    facebook_id: str = None
    token: bytes = None
    name: str = None
    first_name: str = None
    last_name: str = None
    picture: Image = None
    role: str = None
    create_date: datetime = None
    modified_date: datetime = None
    disabled: bool = None
    shop: ShopIn = None


class AccountDb(RwModel):
    id: str = None
    facebook_id: str = None
    token: bytes = None
    name: str = None
    first_name: str = None
    last_name: str = None
    picture: Image = None
    role: str = None
    create_date: datetime = None
    modified_date: datetime = None
    disabled: bool = None
    shop: ShopDb = None







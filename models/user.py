from datetime import datetime

from models.rwmodel import RwModel
from models.shop import ShopIn, ShopOut, ShopDb
from models.image import Image


class UserOut(RwModel):
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


class UserIn(RwModel):
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


class UserDb(RwModel):
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






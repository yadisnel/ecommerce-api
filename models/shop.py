from typing import List

from models.image import Image
from models.location import Location
from models.rwmodel import RwModel


class ShopIn(RwModel):
    name: str = None
    images: List[Image] = None
    location: Location = None
    province_id: str = None
    province_name: str = None


class ShopOut(RwModel):
    id: str = None
    name: str = None
    images: List[Image] = None
    location: Location = None
    province_id: str = None
    province_name: str = None


class ShopDb(RwModel):
    id: str = None
    name: str = None
    images: List[Image] = None
    location: Location = None
    province_id: str = None
    province_name: str = None

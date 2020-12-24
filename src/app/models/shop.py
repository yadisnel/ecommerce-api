from typing import List

from src.app.models.image import Image, Image
from src.app.models.location import Location
from src.app.models.rwmodel import RwModel


class ShopIn(RwModel):
    name: str = None
    images: List[Image] = None
    location: Location = None
    province_id: str = None
    province_name: str = None


class ShopOut(RwModel):
    name: str = None
    images: List[Image] = None
    location: Location = None
    province_id: str = None
    province_name: str = None


class ShopDb(RwModel):
    name: str = None
    images: List[Image] = None
    location: Location = None
    province_id: str = None
    province_name: str = None



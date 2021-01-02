from typing import List

from models.images import Image
from models.locations import Location
from models.rwmodels import RwModel


class ShopIn(RwModel):
    name: str = None
    images: List[Image] = None
    location: Location = None
    zone_id: str = None
    zone_name: str = None


class ShopOut(RwModel):
    id: str = None
    name: str = None
    images: List[Image] = None
    location: Location = None
    zone_id: str = None
    zone_name: str = None


class ShopDb(RwModel):
    id: str = None
    name: str = None
    images: List[Image] = None
    location: Location = None
    zone_id: str = None
    zone_name: str = None
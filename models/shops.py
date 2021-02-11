from typing import List

from models.images import ImageDb
from models.locations import Location
from models.rwmodels import RwModel


class ShopIn(RwModel):
    name: str = None
    images: List[ImageDb] = None
    location: Location = None
    zone_id: str = None
    zone_name: str = None
    account_id: str = None
    country_iso_code: str = None


class ShopDb(RwModel):
    id: str = None
    name: str = None
    images: List[ImageDb] = None
    location: Location = None
    zone_id: str = None
    zone_name: str = None
    account_id: str = None


class ShopOut(RwModel):
    id: str = None
    name: str = None
    images: List[ImageDb] = None
    location: Location = None
    zone_id: str = None
    zone_name: str = None
    account_id: str = None
    country_iso_code: str = None






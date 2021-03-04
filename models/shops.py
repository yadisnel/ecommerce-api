from typing import List

from models.images import ImageDb
from models.rwmodels import RwModel


class ShopIn(RwModel):
    name: str = None
    account_id: str = None
    images: List[ImageDb] = None
    location: List[float] = None
    zone_id: str = None
    zone_name: str = None
    country_iso_code: str = None
    enabled: bool = None


class ShopDb(RwModel):
    id: str = None
    account_id: str = None
    name: str = None
    images: List[ImageDb] = None
    location: List[float] = None
    zone_id: str = None
    zone_name: str = None
    country_iso_code: str = None
    enabled: bool = None


class ShopOut(RwModel):
    id: str = None
    account_id: str = None
    name: str = None
    images: List[ImageDb] = None
    location: List[float] = None
    zone_id: str = None
    zone_name: str = None
    country_iso_code: str = None
    enabled: bool = None







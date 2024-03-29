from models.rwmodels import RwModel
from typing import List
from models.images import ImageDb
from models.locations import Location
from datetime import datetime


class ProductIn(RwModel):
    local_id: str = None
    user_id: str = None
    name: str = None
    description: str = None
    category_id: str = None
    category_name: str = None
    sub_category_id: str = None
    sub_category_name: str = None
    zone_id: str = None
    zone_name: str = None
    price: float = None
    images: List[ImageDb] = None
    isNew: bool = None
    currency: str = None
    created: datetime = None
    modified: datetime = None
    location: Location = None
    promoted: bool = None
    likes: int = None
    views: int = None
    score: float = None
    deleted: bool = None
    country_iso_code: str = None


class ProductDb(RwModel):
    id: str = None
    local_id: str = None
    user_id: str = None
    name: str = None
    description: str = None
    category_id: str = None
    category_name: str = None
    sub_category_id: str = None
    sub_category_name: str = None
    zone_id: str = None
    zone_name: str = None
    price: float = None
    images: List[ImageDb] = None
    isNew: bool = None
    currency: str = None
    created: datetime = None
    modified: datetime = None
    location: Location = None
    promoted: bool = None
    favorite: bool = None
    likes: int = None
    views: int = None
    score: float = None
    deleted: bool = None
    country_iso_code: str = None


class ProductOut(RwModel):
    id: str = None
    user_id: str = None
    local_id: str = None
    name: str = None
    description: str = None
    category_id: str = None
    category_name: str = None
    sub_category_id: str = None
    sub_category_name: str = None
    zone_id: str = None
    zone_name: str = None
    price: float = None
    images: List[ImageDb] = None
    isNew: bool = None
    currency: str = None
    created: datetime = None
    modified: datetime = None
    location: Location = None
    promoted: bool = None
    favorite: bool = None
    likes: int = None
    views: int = None
    score: float = None
    deleted: bool = None


class ProductFavoriteIn(RwModel):
    user_id: str = None
    product_id: str = None
    favorite: bool = None
    country_iso_code: str = None


class ProductFavoriteDb(RwModel):
    id: str = None
    user_id: str = None
    product_id: str = None
    favorite: bool = None
    country_iso_code: str = None


class ProductFavoriteOut(RwModel):
    id: str = None
    user_id: str = None
    product_id: str = None
    favorite: bool = None



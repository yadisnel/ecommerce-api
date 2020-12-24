from src.app.models.rwmodel import RwModel
from typing import List
from src.app.models.image import Image
from src.app.models.location import Location
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
    province_id: str = None
    province_name: str = None
    price: float = None
    images: List[Image] = None
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
    province_id: str = None
    province_name: str = None
    price: float = None
    images: List[Image] = None
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
    province_id: str = None
    province_name: str = None
    price: float = None
    images: List[Image] = None
    isNew: bool = None
    currency: str = None
    created: datetime = None
    modified: datetime = None
    location: Location = None
    promoted: bool = None
    favorited: bool =None
    likes: int = None
    views: int = None
    score: float = None
    deleted: bool = None


class ProductFavoritedIn(RwModel):
    user_id: str = None
    product_id: str = None
    favorited: bool = None


class ProductFavoritedOut(RwModel):
    id: str = None
    user_id: str = None
    product_id: str = None
    favorited: bool = None



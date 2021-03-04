from models.rwmodels import RwModel
from typing import List
from datetime import datetime


class SubCategoryIn(RwModel):
    id: str = None
    name: str = None
    enabled: bool = None

class SubCategoryDb(RwModel):
    id: str = None
    name: str = None
    enabled: bool = None


class SubCategoryOut(RwModel):
    id: str = None
    name: str = None
    enabled: bool = None


class CategoryIn(RwModel):
    name: str = None
    order_n: int = 0
    sub_categories: List[SubCategoryIn] = None
    created: datetime = None
    modified: datetime = None
    country_iso_code: str = None
    enabled: bool = None


class CategoryDb(RwModel):
    id: str = None
    name: str = None
    order_n: int = 0
    sub_categories: List[SubCategoryDb] = None
    created: datetime = None
    modified: datetime = None
    country_iso_code: str = None
    enabled: bool = None


class CategoryOut(RwModel):
    id: str = None
    name: str = None
    order_n: int = 0
    sub_categories: List[SubCategoryOut] = None
    created: datetime = None
    modified: datetime = None


class SyncCategoriesOut(RwModel):
    categories: List[CategoryOut] = None
    is_last_offset: bool = None

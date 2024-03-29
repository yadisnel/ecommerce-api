from models.rwmodels import RwModel
from typing import List
from datetime import datetime


class SubCategoryIn(RwModel):
    id: str = None
    name: str = None


class SubCategoryOut(RwModel):
    id: str = None
    name: str = None


class CategoryIn(RwModel):
    name: str = None
    n_order: int = 0
    sub_categories: List[SubCategoryIn] = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None
    country_iso_code: str = None


class CategoryDb(RwModel):
    id: str = None
    name: str = None
    n_order: int = 0
    sub_categories: List[SubCategoryOut] = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None
    country_iso_code: str = None


class CategoryOut(RwModel):
    id: str = None
    name: str = None
    n_order: int = 0
    sub_categories: List[SubCategoryOut] = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None


class SyncCategoriesOut(RwModel):
    categories: List[CategoryOut] = None
    is_last_offset: bool = None

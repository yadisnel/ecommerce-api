from src.app.models.rwmodel import RwModel
from typing import List
from datetime import datetime


class SubCategoryIn(RwModel):
    id: str = None
    name: str = None


class SubCategoryOut(RwModel):
    id: str = None
    name: str = None


class CategoryIn(RwModel):
    local_id: str = None
    name: str = None
    n_order: int = 0
    sub_categories: List[SubCategoryIn] = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None


class CategoryOut(RwModel):
    id: str = None
    local_id: str = None
    name: str = None
    n_order: int = 0
    sub_categories: List[SubCategoryOut] = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None


class SyncCategoriesOut(RwModel):
    categories: List[CategoryOut] = None
    is_last_offset: bool = None

from src.app.models.rwmodel import RwModel
from datetime import datetime
from typing import List


class ProvinceIn(RwModel):
    name: str = None
    n_order: int = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None


class ProvinceOut(RwModel):
    id: str = None
    name: str = None
    n_order: int = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None


class SyncProvincesOut(RwModel):
    provinces: List[ProvinceOut] = None
    is_last_offset: bool = None


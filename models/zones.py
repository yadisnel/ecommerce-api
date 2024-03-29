from models.rwmodels import RwModel
from datetime import datetime
from typing import List


class ZoneIn(RwModel):
    name: str = None
    order_n: int = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None
    country_iso_code: str = None


class ZoneDb(RwModel):
    id: str = None
    name: str = None
    order_n: int = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None
    country_iso_code: str = None


class ZoneOut(RwModel):
    id: str = None
    name: str = None
    order_n: int = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None


class SyncZonesOut(RwModel):
    zones: List[ZoneOut] = None
    is_last_offset: bool = None


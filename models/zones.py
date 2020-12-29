from models.rwmodels import RwModel
from datetime import datetime
from typing import List


class ZoneIn(RwModel):
    name: str = None
    n_order: int = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None


class ZoneOut(RwModel):
    id: str = None
    name: str = None
    n_order: int = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None


class SyncZonesOut(RwModel):
    zones: List[ZoneOut] = None
    is_last_offset: bool = None


from models.rwmodels import RwModel
from datetime import datetime
from typing import List


class CountryIn(RwModel):
    name: str = None
    n_order: int = None
    country_iso_code: str = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None


class CountryDb(RwModel):
    id: str = None
    name: str = None
    n_order: int = None
    country_iso_code: str = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None


class CountryOut(RwModel):
    id: str = None
    name: str = None
    n_order: int = None
    country_iso_code: str = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None


class SyncCountriesOut(RwModel):
    countries: List[CountryOut] = None
    is_last_offset: bool = None


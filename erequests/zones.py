from datetime import datetime
from pydantic import Field
from models.rwmodels import RwModel


class RequestAddZone(RwModel):
    name: str = Field(..., title="Zone name")
    order_n: int = Field(..., title="Zone order number", ge=0)
    country_iso_code: str = Field(..., title="Country ISO code")


class RequestUpdateZone(RwModel):
    name: str = Field(..., title="Zone name")
    order_n: int = Field(..., title="Zone order number", ge=0)
    deleted: bool = Field(..., title="Zone is deleted")


class RequestSyncZones(RwModel):
    is_db_new: bool = Field(..., title="The client database is new.")
    last_offset: datetime = Field(..., title="Last offset on client.")


class RequestFilterZones(RwModel):
    load_deleted: bool=Field(..., title="Load deleted zones.")
    load_not_deleted: bool = Field(..., title="Load not deleted zones.")
    country_iso_code: str = Field(..., title="Country ISO code")


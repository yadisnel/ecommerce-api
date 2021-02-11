from datetime import datetime
from pydantic import Field
from models.rwmodels import RwModel


class RequestAddZone(RwModel):
    name: str = Field(..., title="Zone name")
    order_n: int = Field(..., title="Zone order number", ge=0)


class RequestUpdateZone(RwModel):
    name: str = Field(..., title="Zone name")
    order_n: int = Field(..., title="Zone order number", ge=0)


class RequestSyncZones(RwModel):
    is_db_new: bool = Field(..., title="The client database is new.")
    last_offset: datetime = Field(..., title="Last offset on client.")

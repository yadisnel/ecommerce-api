from datetime import datetime

from pydantic import Field

from models.rwmodel import RwModel


class RequestAddProvince(RwModel):
    name: str = Field(..., title="Province's name")
    order: int = Field(..., title="Province's order", ge=0)


class RequestUpdateProvince(RwModel):
    name: str = Field(..., title="Province's name")
    order: int = Field(..., title="Province's order", ge=0)


class RequestSyncProvinces(RwModel):
    is_db_new: bool= Field(..., title="The client database is new.")
    last_offset: datetime = Field(..., title="Last offset on client.")
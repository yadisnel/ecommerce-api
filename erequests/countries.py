from datetime import datetime
from pydantic import Field
from models.rwmodels import RwModel


class RequestAddCountry(RwModel):
    name: str = Field(..., title="Country name")
    country_iso_code: str = Field(..., title="Country ISO code", ge=0)


class RequestUpdateCountry(RwModel):
    id: str = Field(..., title="Country id")
    name: str = Field(..., title="Country name")
    order_n: int = Field(..., title="Country order_n", ge=0)
    country_iso_code: str = Field(..., title="Country ISO code", ge=0)


class RequestSyncCountries(RwModel):
    is_db_new: bool= Field(..., title="The client database is new.")
    last_offset: datetime = Field(..., title="Last offset on client.")

from datetime import datetime
from pydantic import Field
from models.rwmodels import RwModel


class RequestAddCountry(RwModel):
    order_n: int = Field(..., title="Country order_n", ge=0)
    country_iso_code: str = Field(..., title="Country ISO code")


class RequestEnableDisableCountry(RwModel):
    enabled: bool = Field(..., title="Country is enabled")


class RequestUpdateCountry(RwModel):
    name: str = Field(..., title="Country name")
    order_n: int = Field(..., title="Country order_n", ge=0)


class RequestSyncCountries(RwModel):
    is_db_new: bool= Field(..., title="The client database is new.")
    last_offset: datetime = Field(..., title="Last offset on client.")


class RequestFilterCountries(RwModel):
    load_disabled: bool=Field(..., title="Load disabled countries.")
    load_enabled: bool = Field(..., title="Load enabled countries.")


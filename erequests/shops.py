from pydantic import Field

from models.rwmodels import RwModel
from erequests.locations import RequestLocation


class RequestAddShop(RwModel):
    name: str = Field(..., title="Shop's name")
    zone_id: str = Field(..., title="Zone id")
    location: RequestLocation = Field(None, title="GPS location.")


class RequestUpdateShop(RwModel):
    name: str = Field(..., title="Shop's name")
    zone_id: str = Field(..., title="Zone id")
    location: RequestLocation = Field(None, title="GPS location.")


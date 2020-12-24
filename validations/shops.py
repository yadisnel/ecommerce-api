from pydantic import Field

from models.rwmodel import RwModel
from validations.locations import RequestLocation


class RequestUpdateShop(RwModel):
    name: str = Field(..., title="Shop's name")
    province_id: str = Field(..., title="Province's id")
    location: RequestLocation = Field(None, title="GPS location.")
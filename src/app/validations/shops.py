from pydantic import Field

from src.app.models.rwmodel import RwModel
from src.app.validations.locations import RequestLocation


class RequestUpdateShop(RwModel):
    name: str = Field(..., title="Shop's name")
    province_id: str = Field(..., title="Province's id")
    location: RequestLocation = Field(None, title="GPS location.")


class RequestDeleteImageFromShop(RwModel):
    image_id: str = Field(..., title="Image's id")

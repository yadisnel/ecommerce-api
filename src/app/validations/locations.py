from pydantic import Field

from src.app.models.rwmodel import RwModel


class RequestLocation(RwModel):
    lat: float = Field(..., title="Location's latitude", ge=-90, le=90)
    long: float = Field(..., title="Location's longitude", ge=-180, le=180)
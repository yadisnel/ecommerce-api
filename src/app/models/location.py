from src.app.models.rwmodel import RwModel
from typing import List


class Location(RwModel):
    type: str = None
    coordinates: List[float] = None

from models.rwmodels import RwModel
from typing import List


class Location(RwModel):
    type: str = None
    coordinates: List[float] = None

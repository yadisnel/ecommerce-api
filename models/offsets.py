from models.rwmodels import RwModel
from datetime import datetime


class Offsets(RwModel):
    zones_offset: datetime = None
    categories_offset: datetime = None


from src.app.models.rwmodel import RwModel
from datetime import datetime


class Offsets(RwModel):
    provinces_offset: datetime = None
    categories_offset: datetime = None


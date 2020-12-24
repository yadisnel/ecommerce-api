from src.app.models.rwmodel import RwModel
from typing import List
from src.app.models.image import Image
from src.app.models.location import Location
from datetime import datetime


class MqttPayload(RwModel):
    payload_type: str = None
    payload: str = None

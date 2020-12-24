from src.app.models.rwmodel import RwModel
from datetime import datetime


class ConversationIn(RwModel):
    user_id_1: str = None
    user_id_2: str = None
    user_id_1_out: bool = None
    user_id_2_out: bool = None
    created: datetime = None
    modified: datetime = None


class ConversationOut(RwModel):
    id: str = None
    user_id_1: str = None
    user_id_2: str = None
    user_id_1_out: bool = None
    user_id_2_out: bool = None
    created: datetime = None
    modified: datetime = None




from src.app.models.rwmodel import RwModel
from datetime import datetime
from typing import Dict


class MessageIn(RwModel):
    user_owner_id: str = None
    conversation_id: str = None
    from_user_id: str = None
    from_user_name: str = None
    to_user_id: str = None
    to_user_name: str = None
    body:Dict = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None


class MessageOut(RwModel):
    id: str= None
    user_owner_id: str = None
    conversation_id: str = None
    from_user_id: str = None
    from_user_name: str = None
    to_user_id: str = None
    to_user_name: str = None
    body:Dict = None
    created: datetime = None
    modified: datetime = None
    deleted: bool = None




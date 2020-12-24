from pydantic import Field

from src.app.models.rwmodel import RwModel
from typing import Dict


class RequestSendMessage(RwModel):
    to_user_id: str =Field(..., title="To user id")
    body: Dict =Field(..., title="Message's body")


class RequestRemoveMessage(RwModel):
    message_id: str = Field(..., title="Message's id")

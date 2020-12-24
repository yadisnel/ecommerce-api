from pydantic import Field

from models.rwmodel import RwModel
from typing import Dict


class RequestSendMessage(RwModel):
    to_user_id: str =Field(..., title="To user id")
    body: Dict =Field(..., title="Message's body")
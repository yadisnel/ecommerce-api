from pydantic import Field

from models.rwmodel import RwModel


class RequestRemoveConversation(RwModel):
    conversation_id: str = Field(..., title="Conversation's id")

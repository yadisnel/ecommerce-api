from pydantic import Field

from src.app.models.rwmodel import RwModel


class RequestRemoveConversation(RwModel):
    conversation_id: str = Field(..., title="Conversation's id")

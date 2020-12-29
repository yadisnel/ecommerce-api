from pydantic import Field

from models.rwmodels import RwModel


class RequestRemoveConversation(RwModel):
    conversation_id: str = Field(..., title="Conversation's id")

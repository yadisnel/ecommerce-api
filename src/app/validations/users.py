from pydantic import Field

from src.app.models.rwmodel import RwModel


class RequestEnableUser(RwModel):
    userId: str = Field(..., title="User id.")


class RequestDisableUser(RwModel):
    userId: str = Field(..., title="User id.")

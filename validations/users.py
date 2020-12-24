from pydantic import Field

from models.rwmodel import RwModel


class RequestEnableUser(RwModel):
    userId: str = Field(..., title="User id.")


class RequestDisableUser(RwModel):
    userId: str = Field(..., title="User id.")

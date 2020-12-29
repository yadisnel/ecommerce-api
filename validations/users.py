from pydantic import Field

from models.rwmodels import RwModel


class RequestEnableUser(RwModel):
    userId: str = Field(..., title="User id.")


class RequestDisableUser(RwModel):
    userId: str = Field(..., title="User id.")

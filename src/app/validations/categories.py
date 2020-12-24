from pydantic import Field

from src.app.models.rwmodel import RwModel


class RequestAddCategory(RwModel):
    local_id: str = Field(..., title="Category's local id")
    name: str = Field(..., title="Category's name")


class RequestAddSubCategory(RwModel):
    name: str = Field(..., title="Sub-category's name")

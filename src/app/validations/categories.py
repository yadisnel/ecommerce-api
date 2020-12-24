from pydantic import Field

from src.app.models.rwmodel import RwModel


class RequestAddCategory(RwModel):
    local_id: str = Field(..., title="Category's local id")
    name: str = Field(..., title="Category's name")


class RequestRemoveCategory(RwModel):
    category_id: str = Field(..., title="Category's id")


class RequestAddSubCategory(RwModel):
    category_id: str = Field(..., title="Category's id")
    name: str = Field(..., title="Sub-category's name")


class RequestRemoveSubCategory(RwModel):
    category_id: str = Field(..., title="Category's id")
    sub_category_id: str = Field(..., title="sub category's id")

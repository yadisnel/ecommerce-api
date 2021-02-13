from pydantic import Field

from models.rwmodels import RwModel


class RequestAddCategory(RwModel):
    order_n: int = Field(..., title="Category's order_n")
    name: str = Field(..., title="Category's name")
    country_iso_code: str = Field(..., title="Country ISO code")


class RequestAddSubCategory(RwModel):
    name: str = Field(..., title="Sub-category's name")


class RequestListCategories(RwModel):
    country_iso_code: str = Field(..., title="Country iso code")

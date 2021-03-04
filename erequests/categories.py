from pydantic import Field

from models.rwmodels import RwModel


class RequestAddCategory(RwModel):
    order_n: int = Field(..., title="Category's order_n")
    name: str = Field(..., title="Category's name")
    country_iso_code: str = Field(..., title="Country ISO code")


class RequestAddSubCategory(RwModel):
    name: str = Field(..., title="Sub-category's name")


class RequestEnableDisableCategory(RwModel):
    enabled: bool = Field(..., title="Category is enabled")


class RequestEnableDisableSubCategory(RwModel):
    enabled: bool = Field(..., title="Sub category is enabled")


class RequestFilterCategories(RwModel):
    load_enabled: bool = Field(..., title="Load enabled zones.")
    load_disabled: bool = Field(..., title="Load disabled zones.")
    country_iso_code: str = Field(..., title="Country ISO code")

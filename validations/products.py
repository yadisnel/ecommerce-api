from pydantic import Field

from models.rwmodels import RwModel
from models.locations import Location


class RequestAddProduct(RwModel):
    local_id: str = Field(..., title="Product's  local id")
    name: str = Field(..., title="Product's  name")
    description: str = Field(..., title="Product's  description")
    category_id: str = Field(..., title="Product's  category id")
    sub_category_id: str = Field(..., title="Product's  sub-category id")
    price: float = Field(..., title="Product's  price in cents", gt=0)
    isNew: bool= Field(..., title="Is new")
    currency: str= Field(..., title="Currency", regex="^(CUP|CUC|EUR|USD)$")


class RequestUpdateProduct(RwModel):
    name: str = Field(..., title="Product's  name")
    description: str = Field(..., title="Product's  description")
    category_id: str = Field(..., title="Product's  category id")
    sub_category_id: str = Field(..., title="Product's  sub-category id")
    price: float = Field(..., title="Product's  price in cents", gt=0)
    isNew: bool= Field(..., title="Is new")
    currency: str= Field(..., title="Currency", regex="^(CUP|CUC)$")


class RequestRemoveProduct(RwModel):
    product_id: str = Field(..., title="Product's id")


class RequestRemoveImageFromProduct(RwModel):
    product_id: str = Field(..., title="Product's id")
    image_id: str = Field(..., title="Image's id")


class RequestSearchProducts(RwModel):
    own: bool  = Field(None, title="Only own products")
    text_search: str = Field(None, title="Text search")
    zone_id: str = Field(None, title="Zone id")
    near: Location = Field(None, title="Near location")
    near_radius: float = Field(None, title="Near radius")
    category_id: str = Field(None, title="Category id")
    sub_category_id: str = Field(None, title="Sub-category id")
    min_price: float = Field(None, title="Min price", ge=1)
    max_price: float = Field(None, title="Max price",ge=1)


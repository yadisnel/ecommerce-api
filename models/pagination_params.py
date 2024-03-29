from pydantic import Field

from models.rwmodels import RwModel


class PaginationParams(RwModel):
    pages: int = Field(None, title="How many pages")
    elements: int = Field(None, title="How many elements per page.")
    total: int = Field(None, title="Total.")

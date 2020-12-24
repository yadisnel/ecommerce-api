from pydantic import Field

from src.app.models.rwmodel import RwModel


class PaginationParams(RwModel):
    pages: int = Field(None, title="How many pages")
    elements: int = Field(None, title="How many elements per page.")
    total: int = Field(None, title="Total.")

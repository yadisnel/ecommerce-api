from pydantic import Field

from src.app.models.rwmodel import RwModel


class RequestPagination(RwModel):
    page: int = Field(..., title="The page number. Begin in 1", gt=0)
    elements: int = Field(..., title="How many elements per page.", gt=0)


class RequestPaginationParams(RwModel):
    elements: int = Field(..., title="Elements per page.", gt=0)

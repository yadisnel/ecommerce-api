from datetime import datetime

from pydantic import Field

from models.rwmodel import RwModel


class RequestSync(RwModel):
    is_db_new: bool= Field(..., title="The client database is new.")
    last_offset: datetime = Field(..., title="Last offset on client.")

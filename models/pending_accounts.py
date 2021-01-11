from datetime import datetime

from models.rwmodels import RwModel


class StandardPendingAccountIn(RwModel):
    email: str = None
    created_at: datetime = None
    modified_at: datetime = None
    hashed_password: str = None
    security_code: str = None


class StandardPendingAccountDB(RwModel):
    id: str = None
    email: str = None
    created_at: datetime = None
    modified_at: datetime = None
    hashed_password: str = None
    security_code: str = None









from src.app.models.rwmodel import RwModel


class Token(RwModel):
    access_token: str
    token_type: str

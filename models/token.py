from models.rwmodel import RwModel


class Token(RwModel):
    access_token: str
    token_type: str

from models.rwmodels import RwModel


class Token(RwModel):
    access_token: str
    token_type: str


class TokenData(RwModel):
    username: str = None

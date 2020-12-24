from src.app.models.rwmodel import RwModel


class Image(RwModel):
    id: str = None
    original_key: str = None
    original_width: int = None
    original_height: int = None
    original_size: int = None
    original_url: str = None
    thumb_key: str = None
    thumb_width: int = None
    thumb_height: int = None
    thumb_size: int = None
    thumb_url: str = None


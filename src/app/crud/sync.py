from src.app.core.mongodb import AsyncIOMotorClient
from src.app.crud.provinces import get_provinces_offset_impl
from src.app.crud.categories import get_categories_offset_impl
from src.app.models.offset import Offsets


async def get_offsets_impl(conn: AsyncIOMotorClient) -> Offsets:
    offsets: Offsets = Offsets()
    offsets.provinces_offset = await get_provinces_offset_impl(conn=conn)
    offsets.categories_offset = await get_categories_offset_impl(conn=conn)
    return offsets

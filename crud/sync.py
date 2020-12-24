from core.mongodb import AsyncIOMotorClient
from crud.provinces import get_provinces_offset_impl
from crud.categories import get_categories_offset_impl
from models.offset import Offsets


async def get_offsets_impl(conn: AsyncIOMotorClient) -> Offsets:
    offsets: Offsets = Offsets()
    offsets.provinces_offset = await get_provinces_offset_impl(conn=conn)
    offsets.categories_offset = await get_categories_offset_impl(conn=conn)
    return offsets

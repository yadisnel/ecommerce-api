from core.mongodb import AsyncIOMotorClient
from crud.zones import get_zones_offset_impl
from crud.categories import get_categories_offset_impl
from models.offsets import Offsets


async def get_offsets_impl(conn: AsyncIOMotorClient) -> Offsets:
    offsets: Offsets = Offsets()
    offsets.zones_offset = await get_zones_offset_impl(conn=conn)
    offsets.categories_offset = await get_categories_offset_impl(conn=conn)
    return offsets

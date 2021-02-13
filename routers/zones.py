from typing import List
from fastapi import APIRouter
from fastapi import Depends
from crud.zones import get_all_zones_impl
from core.mongodb import AsyncIOMotorClient
from core.mongodb import get_database
from models.zones import ZoneOut

router = APIRouter()


@router.get("/zones", response_model=List[ZoneOut])
async def list_zones(conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_zones_impl(conn=conn)

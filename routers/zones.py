from typing import List

from fastapi import APIRouter
from fastapi import Depends

from crud.zones import get_all_zones_impl
from core.mongodb import AsyncIOMotorClient, get_database
from models.zones import ZoneOut
from models.accounts import AccountDb
from routers.accounts import get_current_active_user

router = APIRouter()


@router.get("/zones", response_model=List[ZoneOut])
async def list_zones(current_user: AccountDb = Depends(get_current_active_user),
                         conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_zones_impl(conn=conn)
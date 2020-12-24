from typing import List

from fastapi import APIRouter
from fastapi import Depends, Body

from src.app.crud.provinces import get_all_provinces_impl, sync_provinces_impl
from src.app.core.mongodb import AsyncIOMotorClient, get_database
from src.app.models.province import ProvinceOut
from src.app.models.user import UserDb
from src.app.routers.users import get_current_active_user
from src.app.models.province import SyncProvincesOut
from src.app.validations.sync import RequestSync

router = APIRouter()


@router.post("/provinces/get-all-provinces", response_model=List[ProvinceOut])
async def get_all_provinces(current_user: UserDb = Depends(get_current_active_user),
                            conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_provinces_impl(conn=conn)


@router.post("/provinces/sync-provinces", response_model=SyncProvincesOut)
async def sync_provinces(current_user: UserDb = Depends(get_current_active_user),
                         req: RequestSync = Body(..., title="Last change"),
                         conn: AsyncIOMotorClient = Depends(get_database)):
    return await sync_provinces_impl(req=req, conn=conn)
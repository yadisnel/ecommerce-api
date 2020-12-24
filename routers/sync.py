from fastapi import APIRouter
from fastapi import Depends, Body

from core.mongodb import AsyncIOMotorClient, get_database
from crud.sync import get_offsets_impl
from models.offset import Offsets
from models.user import UserDb
from routers.users import get_current_active_user
from crud.categories import sync_categories_impl
from crud.categories import SyncCategoriesOut
from validations.sync import RequestSync
from models.province import SyncProvincesOut
from crud.provinces import sync_provinces_impl


router = APIRouter()


@router.get("/sync/offsets/", response_model=Offsets)
async def get_offsets(current_user: UserDb = Depends(get_current_active_user),
                      conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_offsets_impl(conn=conn)


@router.get("/sync/categories/", response_model=SyncCategoriesOut)
async def sync_categories(current_user: UserDb = Depends(get_current_active_user),
                         req: RequestSync = Body(..., title="Last change"),
                         conn: AsyncIOMotorClient = Depends(get_database)):
    return await sync_categories_impl(req=req, conn=conn)


@router.get("/sync/provinces/", response_model=SyncProvincesOut)
async def sync_provinces(current_user: UserDb = Depends(get_current_active_user),
                         req: RequestSync = Body(..., title="Last change"),
                         conn: AsyncIOMotorClient = Depends(get_database)):
    return await sync_provinces_impl(req=req, conn=conn)

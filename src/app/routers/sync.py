from fastapi import APIRouter
from fastapi import Depends, Body

from src.app.core.mongodb import AsyncIOMotorClient, get_database
from src.app.crud.sync import get_offsets_impl
from src.app.models.offset import Offsets
from src.app.models.user import UserDb
from src.app.routers.users import get_current_active_user
from src.app.crud.categories import sync_categories_impl
from src.app.models.category import SyncCategoriesOut
from src.app.validations.sync import RequestSync
from src.app.models.province import SyncProvincesOut
from src.app.crud.provinces import sync_provinces_impl


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

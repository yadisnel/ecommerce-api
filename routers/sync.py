from fastapi import APIRouter
from fastapi import Depends, Body

from core.mongodb import AsyncIOMotorClient, get_database
from crud.sync import get_offsets_impl
from models.offsets import Offsets
from models.accounts import AccountDb
from routers.accounts import get_current_active_user
from crud.categories import sync_categories_impl
from crud.categories import SyncCategoriesOut
from erequests.sync import RequestSync
from models.zones import SyncZonesOut
from crud.zones import sync_zones_impl


router = APIRouter()


@router.get("/sync/offsets/", response_model=Offsets)
async def get_offsets(current_user: AccountDb = Depends(get_current_active_user),
                      conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_offsets_impl(conn=conn)


@router.get("/sync/categories/", response_model=SyncCategoriesOut)
async def sync_categories(current_user: AccountDb = Depends(get_current_active_user),
                          req: RequestSync = Body(..., title="Last change"),
                          conn: AsyncIOMotorClient = Depends(get_database)):
    return await sync_categories_impl(req=req, conn=conn)


@router.get("/sync/zones/", response_model=SyncZonesOut)
async def sync_zones(current_user: AccountDb = Depends(get_current_active_user),
                         req: RequestSync = Body(..., title="Last change"),
                         conn: AsyncIOMotorClient = Depends(get_database)):
    return await sync_zones_impl(req=req, conn=conn)

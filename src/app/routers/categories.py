from fastapi import APIRouter, Body
from fastapi import Depends

from src.app.core.mongodb import AsyncIOMotorClient, get_database
from src.app.models.category import CategoryOut, SyncCategoriesOut
from src.app.models.user import UserDb
from src.app.routers.users import get_current_active_user
from typing import List
from src.app.crud.categories import get_all_categories_impl, sync_categories_impl
from src.app.validations.sync import RequestSync

router = APIRouter()


@router.post("/categories/get-all-categories", response_model=List[CategoryOut])
async def get_all_categories(current_user: UserDb = Depends(get_current_active_user),
                           conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_categories_impl(conn=conn)


@router.post("/categories/sync-categories", response_model=SyncCategoriesOut)
async def sync_categories(current_user: UserDb = Depends(get_current_active_user),
                         req: RequestSync = Body(..., title="Last change"),
                         conn: AsyncIOMotorClient = Depends(get_database)):
    return await sync_categories_impl(req=req, conn=conn)

from fastapi import APIRouter
from fastapi import Depends

from core.mongodb import AsyncIOMotorClient, get_database
from models.categories import CategoryOut
from models.accounts import AccountDb
from routers.accounts import get_current_active_user
from typing import List
from crud.categories import get_all_categories_impl

router = APIRouter()


@router.get("/categories", response_model=List[CategoryOut])
async def list_categories(current_user: AccountDb = Depends(get_current_active_user),
                          conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_categories_impl(conn=conn)

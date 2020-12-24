from fastapi import APIRouter
from fastapi import Depends

from core.mongodb import AsyncIOMotorClient, get_database
from models.category import CategoryOut
from models.user import UserDb
from routers.users import get_current_active_user
from typing import List
from crud.categories import get_all_categories_impl

router = APIRouter()


@router.get("/categories", response_model=List[CategoryOut])
async def list_categories(current_user: UserDb = Depends(get_current_active_user),
                           conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_categories_impl(conn=conn)

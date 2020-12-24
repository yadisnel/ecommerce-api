from typing import List

from fastapi import APIRouter
from fastapi import Depends

from crud.provinces import get_all_provinces_impl
from core.mongodb import AsyncIOMotorClient, get_database
from models.province import ProvinceOut
from models.user import UserDb
from routers.users import get_current_active_user

router = APIRouter()


@router.get("/provinces", response_model=List[ProvinceOut])
async def list_provinces(current_user: UserDb = Depends(get_current_active_user),
                            conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_provinces_impl(conn=conn)
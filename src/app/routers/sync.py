from fastapi import APIRouter
from fastapi import Depends

from src.app.core.mongodb import AsyncIOMotorClient, get_database
from src.app.crud.sync import get_offsets_impl
from src.app.models.offset import Offsets
from src.app.models.user import UserDb
from src.app.routers.users import get_current_active_user

router = APIRouter()


@router.post("/sync/get-offsets", response_model=Offsets)
async def get_offsets(current_user: UserDb = Depends(get_current_active_user),
                      conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_offsets_impl(conn=conn)

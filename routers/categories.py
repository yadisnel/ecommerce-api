from fastapi import APIRouter
from fastapi import Depends
from fastapi import Body

from core.mongodb import AsyncIOMotorClient, get_database
from erequests.categories import RequestListCategories
from models.categories import CategoryOut
from typing import List
from crud.categories import get_all_categories_impl

router = APIRouter()


@router.get("/categories", response_model=List[CategoryOut])
async def list_categories(request: RequestListCategories = Body(..., title="Message"),
                          conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_categories_impl(request=request, conn=conn)

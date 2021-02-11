from typing import List
from fastapi import APIRouter
from fastapi import Depends
from crud.countries import get_all_countries_impl
from core.mongodb import AsyncIOMotorClient, get_database
from models.countries import CountryOut

router = APIRouter()


@router.get("/countries/", response_model=List[CountryOut])
async def list_countries(conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_countries_impl(conn=conn)

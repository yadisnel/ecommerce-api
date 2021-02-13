from typing import List
from fastapi import APIRouter
from fastapi import Depends
from crud.countries import get_all_countries_impl
from core.mongodb import AsyncIOMotorClient, get_database
from erequests.countries import RequestFilterCountries
from models.countries import CountryOut

router = APIRouter()


@router.post("/countries/search", response_model=List[CountryOut])
async def search_countries(conn: AsyncIOMotorClient = Depends(get_database)):
    filter_countries: RequestFilterCountries = RequestFilterCountries(load_deleted=False,
                                                                      load_not_deleted=True)
    return await get_all_countries_impl(conn=conn, filter_countries=filter_countries)

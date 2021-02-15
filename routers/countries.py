from typing import List
from fastapi import APIRouter
from fastapi import Depends
from crud.countries import get_all_countries_impl
from core.mongodb import AsyncIOMotorClient, get_database
from erequests.countries import RequestFilterCountries
from models.countries import CountryOut, CountryDb

router = APIRouter()


@router.get("/countries", response_model=List[CountryOut])
async def list_countries(conn: AsyncIOMotorClient = Depends(get_database)):
    filter_countries: RequestFilterCountries = RequestFilterCountries(load_deleted=False,
                                                                      load_not_deleted=True)

    countries_db: List[CountryDb] = await get_all_countries_impl(conn=conn, filter_countries=filter_countries)
    countries_out: List[CountryOut] = []
    for country_db in countries_db:
        countries_out.append(CountryOut(**country_db.dict()))
    return countries_out

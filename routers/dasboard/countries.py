from typing import List

from fastapi import Body
from fastapi import HTTPException
from fastapi import Depends, Path
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_404_NOT_FOUND
from starlette.status import HTTP_409_CONFLICT
from starlette.status import HTTP_400_BAD_REQUEST
from core.generics import is_valid_oid
from crud.countries import exists_country_by_iso_code_impl, get_all_countries_impl
from crud.countries import add_country_impl
from crud.countries import exists_country_by_id_impl
from crud.countries import remove_country_by_id_impl
from crud.countries import update_country_impl
from core.mongodb import AsyncIOMotorClient, get_database
from models.countries import CountryOut
from models.accounts import AccountDb
from routers.dasboard.dashboard import router
from routers.accounts import get_current_active_admin_user
from erequests.countries import RequestAddCountry, RequestFilterCountries
from erequests.countries import RequestUpdateCountry


@router.post("/dashboard/countries/", status_code=HTTP_200_OK, response_model=CountryOut)
async def add_country(current_user: AccountDb = Depends(get_current_active_admin_user),
                      e_request: RequestAddCountry = Body(..., title="Country."),
                      conn: AsyncIOMotorClient = Depends(get_database)):
    exists_country: bool = await exists_country_by_iso_code_impl(country_iso_code=e_request.country_iso_code, conn=conn)
    if exists_country:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Country already exist.",
        )
    return await add_country_impl(e_request=e_request, conn=conn)


@router.delete("/dashboard/countries/{country_id}", status_code=HTTP_200_OK)
async def remove_country(current_user: AccountDb = Depends(get_current_active_admin_user),
                         country_id: str = Path(..., title="Country id"),
                         conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=country_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid country id.",
        )
    exists_country: bool = await exists_country_by_id_impl(country_id=country_id, conn=conn)
    if not exists_country:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Country does not exist.",
        )
    await remove_country_by_id_impl(country_id=country_id, conn=conn)
    return {"success": True}


@router.put("/dashboard/countries/{country_id}", status_code=HTTP_200_OK, response_model=CountryOut)
async def update_country(current_user: AccountDb = Depends(get_current_active_admin_user),
                         country_id: str = Path(..., title="Country id"),
                         e_request: RequestUpdateCountry = Body(..., title="Country"),
                         conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=country_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid country id.",
        )
    exists_country: bool = await exists_country_by_id_impl(country_id=country_id, conn=conn)
    if not exists_country:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Country does not exist.",
        )
    return await update_country_impl(country_id=country_id, e_request=e_request, conn=conn)


@router.post("/dashboard/countries/search", response_model=List[CountryOut])
async def search_countries(filter_countries: RequestFilterCountries,
                         current_user: AccountDb = Depends(get_current_active_admin_user),
                         conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_countries_impl(conn=conn, filter_countries=filter_countries)

from typing import List

from fastapi import Body, HTTPException
from fastapi import Depends, Path
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST

from core.generics import is_valid_oid
from crud.countries import exists_country_by_iso_code_impl, add_country_impl, exists_country_by_id_impl, \
    remove_country_by_id_impl, update_country_impl, get_all_countries_impl
from crud.zones import add_zone_impl, remove_zone_by_id_impl
from crud.zones import exists_zone_by_id_impl, exists_zone_by_name_impl
from crud.zones import get_all_zones_impl, update_zone_name_impl
from core.mongodb import AsyncIOMotorClient, get_database
from models.countries import CountryIn
from models.zones import ZoneIn, ZoneOut
from models.accounts import AccountDb
from routers.dasboard.dashboard import router
from routers.accounts import get_current_active_admin_user
from erequests.countries import RequestAddCountry, RequestUpdateCountry
from erequests.zones import RequestAddZone, RequestUpdateZone
from datetime import datetime


@router.post("/dashboard/countries/", response_model=ZoneOut)
async def add_zone(current_user: AccountDb = Depends(get_current_active_admin_user),
                   req: RequestAddCountry = Body(..., title="Country."),
                   conn: AsyncIOMotorClient = Depends(get_database)):
    exists_country: bool = await exists_country_by_iso_code_impl(country_iso_code=req.country_iso_code, conn=conn)
    if exists_country:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Country already exist.",
        )
    country_in: CountryIn = CountryIn()
    country_in.name = req.name
    country_in.country_iso_code = req.country_iso_code
    utc_now: datetime = datetime.utcnow()
    country_in.created = utc_now
    country_in.modified = utc_now
    country_in.deleted = False
    return await add_country_impl(country_in=country_in, conn=conn)


@router.delete("/dashboard/countries/{country_id}", response_model=ZoneOut)
async def remove_zone(current_user: AccountDb = Depends(get_current_active_admin_user),
                      country_id: str = Path(..., title="Country id"),
                      conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=country_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid country id.",
        )
    exists_zone: bool = await exists_country_by_id_impl(country_id=country_id, conn=conn)
    if not exists_zone:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Country does not exist.",
        )
    await remove_country_by_id_impl(country_id=country_id, conn=conn)
    return {"success": True}


@router.put("/dashboard/countries/{country_id}", response_model=ZoneOut)
async def update_zone(current_user: AccountDb = Depends(get_current_active_admin_user),
                      country_id: str = Path(..., title="Country id"),
                      req: RequestUpdateCountry = Body(..., title="Country"),
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
    return await update_country_impl(country_id=country_id, name=req.name, order_n=req.order_n, country_iso_code=req.country_iso_code, conn=conn)


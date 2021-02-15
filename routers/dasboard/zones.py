from typing import List

from fastapi import Body, HTTPException
from fastapi import Depends, Path
from starlette.status import HTTP_409_CONFLICT
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_404_NOT_FOUND

from core.generics import is_valid_oid
from crud.countries import exists_country_by_iso_code_impl, exists_country_by_id_impl
from crud.zones import add_zone_impl, remove_zone_by_id_impl, update_zone_impl, exists_zone_without_deleted_impl, \
    get_all_zones_impl
from crud.zones import exists_zone_by_id_impl, exists_zone_by_name_and_country_iso_code_impl
from core.mongodb import AsyncIOMotorClient, get_database
from models.zones import ZoneIn, ZoneDb
from models.accounts import AccountDb
from routers.dasboard.dashboard import router
from routers.accounts import get_current_active_admin_user
from erequests.zones import RequestAddZone, RequestUpdateZone, RequestFilterZones
from datetime import datetime


@router.post("/dashboard/zones/", response_model=ZoneDb)
async def add_zone(current_user: AccountDb = Depends(get_current_active_admin_user),
                   e_request: RequestAddZone = Body(..., title="Zone."),
                   conn: AsyncIOMotorClient = Depends(get_database)):
    exists_zone: bool = await exists_zone_by_name_and_country_iso_code_impl(name=e_request.name,
                                                                            country_iso_code=e_request.country_iso_code,
                                                                            conn=conn)
    if exists_zone:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Zone already exist.",
        )
    exists_country: bool = await exists_country_by_iso_code_impl(country_iso_code=e_request.country_iso_code, conn=conn)
    if not exists_country:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="country not found.",
        )
    zone_in: ZoneIn = ZoneIn()
    zone_in.name = e_request.name
    zone_in.order_n = e_request.order_n
    utc_now: datetime = datetime.utcnow()
    zone_in.created = utc_now
    zone_in.modified = utc_now
    zone_in.country_iso_code = e_request.country_iso_code
    zone_in.deleted = False
    return await add_zone_impl(zone_in=zone_in, conn=conn)


@router.delete("/dashboard/zones/{zone_id}", status_code=200)
async def remove_zone(current_user: AccountDb = Depends(get_current_active_admin_user),
                      zone_id: str = Path(..., title="Zone id"),
                      conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=zone_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_zone: bool = await exists_zone_by_id_impl(zone_id=zone_id, conn=conn)
    if not exists_zone:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Zone does not exist.",
        )
    await remove_zone_by_id_impl(zone_id=zone_id, conn=conn)
    return {"success": True}


@router.put("/dashboard/zones/{zone_id}", response_model=ZoneDb)
async def update_zone(current_user: AccountDb = Depends(get_current_active_admin_user),
                      zone_id: str = Path(..., title="Zone id"),
                      e_request: RequestUpdateZone = Body(..., title="Zone"),
                      conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=zone_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_zone: bool = await exists_zone_without_deleted_impl(zone_id=zone_id, conn=conn)
    if not exists_zone:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Zone does not exist.",
        )
    return await update_zone_impl(zone_id=zone_id, e_request=e_request, conn=conn)


@router.post("/dashboard/zones/search", response_model=List[ZoneDb])
async def search_zones(filter_zones: RequestFilterZones,
                           current_user: AccountDb = Depends(get_current_active_admin_user),
                           conn: AsyncIOMotorClient = Depends(get_database)):
    exists_country: bool = await exists_country_by_iso_code_impl(country_iso_code=filter_zones.country_iso_code,
                                                                 conn=conn)
    if not exists_country:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Country does not exist.",
        )
    return await get_all_zones_impl(conn=conn, filter_zones=filter_zones)

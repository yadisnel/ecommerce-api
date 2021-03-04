from typing import List

from fastapi import Body, HTTPException
from fastapi import Depends, Path
from starlette.status import HTTP_409_CONFLICT
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_404_NOT_FOUND

from core.generics import is_valid_oid
from crud.countries import exists_country_by_iso_code_include_disabled_impl
from crud.zones import (
    add_zone_impl,
    enable_disable_zone_by_id_impl,
    update_zone_impl,
    exists_zone_inc_disabled_impl,
    search_zones_impl,
    )
from crud.zones import exists_zone_by_id_impl, exists_zone_by_name_and_country_iso_code_impl
from core.mongodb import AsyncIOMotorClient, get_database
from models.zones import ZoneDb
from models.accounts import AccountDb
from routers.dasboard.dashboard import router
from routers.accounts import get_current_active_admin_user
from erequests.zones import RequestAddZone, RequestUpdateZone, RequestFilterZones, RequestEnableDisableZone


@router.post("/dashboard/zones/", response_model=ZoneDb)
async def add_zone(current_user: AccountDb = Depends(get_current_active_admin_user),
                   e_request: RequestAddZone = Body(..., title="Zone."),
                   conn: AsyncIOMotorClient = Depends(get_database)):
    async with await conn.start_session() as s:
        async with s.start_transaction():
            e_request.country_iso_code = e_request.country_iso_code.upper()
            exists_zone: bool = await exists_zone_by_name_and_country_iso_code_impl(name=e_request.name,
                                                                                    country_iso_code=e_request.country_iso_code,
                                                                                    conn=conn)
            if exists_zone:
                raise HTTPException(
                    status_code=HTTP_409_CONFLICT,
                    detail="Zone already exist.",
                    )
            exists_country: bool = await exists_country_by_iso_code_include_disabled_impl(
                country_iso_code=e_request.country_iso_code, conn=conn)
            if not exists_country:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail="country not found.",
                    )
            return await add_zone_impl(e_request=e_request, conn=conn)


@router.delete("/dashboard/zones/{zone_id}", status_code=200)
async def enable_disable_zone(current_user: AccountDb = Depends(get_current_active_admin_user),
                              e_request: RequestEnableDisableZone = Body(..., title="Zone is enabled"),
                              zone_id: str = Path(..., title="Zone id"),
                              conn: AsyncIOMotorClient = Depends(get_database)):
    async with await conn.start_session() as s:
        async with s.start_transaction():
            if not is_valid_oid(oid=zone_id):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid zone id.",
                    )
            exists_zone: bool = await exists_zone_inc_disabled_impl(zone_id=zone_id, conn=conn)
            if not exists_zone:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND,
                    detail="Zone does not exist.",
                    )
            await enable_disable_zone_by_id_impl(e_request=e_request,
                                                 zone_id=zone_id,
                                                 conn=conn)
            return {"success": True}


@router.put("/dashboard/zones/{zone_id}", response_model=ZoneDb)
async def update_zone(current_user: AccountDb = Depends(get_current_active_admin_user),
                      zone_id: str = Path(..., title="Zone id"),
                      e_request: RequestUpdateZone = Body(..., title="Zone"),
                      conn: AsyncIOMotorClient = Depends(get_database)):
    async with await conn.start_session() as s:
        async with s.start_transaction():
            if not is_valid_oid(oid=zone_id):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid category id.",
                    )
            exists_zone: bool = await exists_zone_inc_disabled_impl(zone_id=zone_id, conn=conn)
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
    filter_zones.country_iso_code = filter_zones.country_iso_code.upper()
    exists_country: bool = await exists_country_by_iso_code_include_disabled_impl(
        country_iso_code=filter_zones.country_iso_code,
        conn=conn)
    if not exists_country:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Country does not exist.",
            )
    return await search_zones_impl(conn=conn, filter_zones=filter_zones)

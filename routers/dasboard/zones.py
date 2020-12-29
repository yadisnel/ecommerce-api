from typing import List

from fastapi import Body, HTTPException
from fastapi import Depends, Path
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST

from core.generics import is_valid_oid
from crud.zones import add_zone_impl, remove_zone_by_id_impl
from crud.zones import exists_zone_by_id_impl, exists_zone_by_name_impl
from crud.zones import get_all_zones_impl, update_zone_name_impl
from core.mongodb import AsyncIOMotorClient, get_database
from models.zones import ZoneIn, ZoneOut
from models.accounts import AccountDb
from routers.dasboard.dashboard import router
from routers.accounts import get_current_active_admin_user
from validations.zones import RequestAddZone, RequestUpdateZone
from datetime import datetime


@router.post("/dashboard/zones/", response_model=ZoneOut)
async def add_zone(current_user: AccountDb = Depends(get_current_active_admin_user),
                   req: RequestAddZone = Body(..., title="Zone."),
                   conn: AsyncIOMotorClient = Depends(get_database)):
    exists_zone: bool = await exists_zone_by_name_impl(name=req.name, conn=conn)
    if exists_zone:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Zone already exist.",
        )
    zone_in: ZoneIn = ZoneIn()
    zone_in.name = req.name
    zone_in.order = req.order
    utc_now: datetime = datetime.utcnow()
    zone_in.created = utc_now
    zone_in.modified = utc_now
    zone_in.deleted = False
    return await add_zone_impl(zone_in=zone_in, conn=conn)


@router.delete("/dashboard/zones/{zone_id}", response_model=ZoneOut)
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
            status_code=HTTP_400_BAD_REQUEST,
            detail="Zone does not exist.",
        )
    await remove_zone_by_id_impl(zone_id=zone_id, conn=conn)
    return {"success": True}


@router.put("/dashboard/zones/{zone_id}", response_model=ZoneOut)
async def update_zone(current_user: AccountDb = Depends(get_current_active_admin_user),
                      zone_id: str = Path(..., title="Zone id"),
                      req: RequestUpdateZone = Body(..., title="Zone"),
                      conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=zone_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_zone: bool = await exists_zone_by_id_impl(zone_id=zone_id, conn=conn)
    if not exists_zone:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Zone does not exist.",
        )
    return await update_zone_name_impl(zone_id=zone_id, name=req.name, order=req.order, conn=conn)


@router.get("/dashboard/zones/", response_model=List[ZoneOut])
async def list_zones(current_user: AccountDb = Depends(get_current_active_admin_user),
                     conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_zones_impl(conn=conn)

from typing import List

from fastapi import Body, HTTPException
from fastapi import Depends, Path
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST

from core.generics import is_valid_oid
from crud.zones import add_zone_impl, remove_zone_by_id_impl
from crud.zones import exists_zone_by_id_impl, exists_zone_by_name_and_country_iso_code_impl
from crud.zones import get_all_zones_impl
from core.mongodb import AsyncIOMotorClient, get_database
from models.zones import ZoneIn, ZoneOut
from models.accounts import AccountDb
from routers.dasboard.dashboard import router
from routers.accounts import get_current_active_admin_user
from erequests.zones import RequestAddZone, RequestUpdateZone
from datetime import datetime


@router.get("/dashboard/profiling/functions-duration", response_model=ZoneOut)
async def add_zone(current_user: AccountDb = Depends(get_current_active_admin_user),
                   req: RequestAddZone = Body(..., title="Zone."),
                   conn: AsyncIOMotorClient = Depends(get_database)):
    exists_zone: bool = await exists_zone_by_name_and_country_iso_code_impl(name=req.name, conn=conn)
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


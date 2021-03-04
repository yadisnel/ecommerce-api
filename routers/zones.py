from typing import List
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi import Path
from starlette.status import HTTP_404_NOT_FOUND

from crud.countries import exists_country_by_iso_code_impl
from crud.zones import search_zones_impl
from core.mongodb import AsyncIOMotorClient
from core.mongodb import get_database
from erequests.zones import RequestFilterZones
from models.zones import ZoneOut, ZoneDb

router = APIRouter()


@router.get("/zones/{country_iso_code}", response_model=List[ZoneOut])
async def list_zones(country_iso_code: str = Path(..., title="Country iso code"),
                     conn: AsyncIOMotorClient = Depends(get_database)):
    exists_country: bool = await exists_country_by_iso_code_impl(country_iso_code=country_iso_code,
                                                                 conn=conn)
    if not exists_country:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Country does not exist.",
        )
    filter_zones: RequestFilterZones = RequestFilterZones(load_enabled=True,
                                                          load_disabled=False,
                                                          country_iso_code=country_iso_code)
    zones_db: List[ZoneDb] = await search_zones_impl(conn=conn, filter_zones=filter_zones)
    zones_out: List[ZoneOut] = []
    for zone_db in zones_db:
        zones_out.append(ZoneOut(**zone_db.dict()))
    return zones_out

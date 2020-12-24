from typing import List

from fastapi import Body, HTTPException
from fastapi import Depends, Path
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST

from src.app.core.generics import is_valid_oid
from src.app.crud.provinces import add_province_impl, remove_province_by_id_impl
from src.app.crud.provinces import exists_province_by_id_impl, exists_province_by_name_impl
from src.app.crud.provinces import get_all_provinces_impl, update_province_name_impl
from src.app.core.mongodb import AsyncIOMotorClient, get_database
from src.app.models.province import ProvinceIn, ProvinceOut
from src.app.models.user import UserDb
from src.app.routers.dasboard.dashboard import router
from src.app.routers.users import get_current_active_admin_user
from src.app.validations.provinces import RequestAddProvince,RequestUpdateProvince
from datetime import datetime


@router.post("/dashboard/provinces/", response_model=ProvinceOut)
async def add_province(current_user: UserDb = Depends(get_current_active_admin_user),
                       req: RequestAddProvince = Body(..., title="Province"),
                       conn: AsyncIOMotorClient = Depends(get_database)):
    exists_province: bool = await exists_province_by_name_impl(name=req.name, conn=conn)
    if exists_province:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Province already exist.",
        )
    province_in: ProvinceIn = ProvinceIn()
    province_in.name = req.name
    province_in.order = req.order
    utc_now: datetime = datetime.utcnow()
    province_in.created = utc_now
    province_in.modified = utc_now
    province_in.deleted = False
    return await add_province_impl(province_in=province_in, conn=conn)


@router.delete("/dashboard/provinces/{province_id}", response_model=ProvinceOut)
async def remove_province(current_user: UserDb = Depends(get_current_active_admin_user),
                          province_id: str = Path(..., title="Province's id"),
                          conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=province_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_province: bool = await exists_province_by_id_impl(province_id=province_id, conn=conn)
    if not exists_province:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Province does not exist.",
        )
    await remove_province_by_id_impl(province_id=province_id, conn=conn)
    return {"success": True}


@router.put("/dashboard/provinces/{province_id}", response_model=ProvinceOut)
async def update_province(current_user: UserDb = Depends(get_current_active_admin_user),
                          province_id: str = Path(..., title="Province's id"),
                          req: RequestUpdateProvince = Body(..., title="Province"),
                          conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=province_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_province: bool = await exists_province_by_id_impl(province_id=province_id, conn=conn)
    if not exists_province:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Province does not exist.",
        )
    return await update_province_name_impl(province_id=province_id,name=req.name,order = req.order, conn=conn)


@router.get("/dashboard/provinces/", response_model=List[ProvinceOut])
async def list_provinces(current_user: UserDb = Depends(get_current_active_admin_user),
                            conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_provinces_impl(conn=conn)

from fastapi import Body, HTTPException
from fastapi import Depends, Path
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST
from typing import List

from core.generics import is_valid_oid
from crud.categories import add_category_impl, add_sub_category_impl, remove_category_by_id_impl
from crud.categories import exists_sub_category_by_name_impl, exists_category_by_name_impl, exists_category_by_id_impl
from crud.categories import remove_sub_category_impl, exists_sub_category_by_id_impl
from core.mongodb import AsyncIOMotorClient, get_database
from models.categories import CategoryIn, CategoryOut, SubCategoryIn
from models.accounts import AccountDb
from routers.dasboard.dashboard import router
from routers.accounts import get_current_active_admin_user
from erequests.categories import RequestAddCategory, RequestAddSubCategory
import uuid
import os
from datetime import datetime


@router.post("/dashboard/categories/", response_model=CategoryOut)
async def add_category(current_user: AccountDb = Depends(get_current_active_admin_user),
                       e_request: RequestAddCategory = Body(..., title="Category"),
                       conn: AsyncIOMotorClient = Depends(get_database)):
    exists_category: bool = await exists_category_by_name_impl(name=e_request.name, conn=conn)
    if exists_category:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Category already exist.",
        )
    category_in: CategoryIn = CategoryIn()
    category_in.name = e_request.name
    category_in.sub_categories = []
    utc_now: datetime = datetime.utcnow()
    category_in.created = utc_now
    category_in.modified = utc_now
    category_in.country_iso_code = e_request.country_iso_code
    category_in.deleted = False
    return await add_category_impl(category_in=category_in, conn=conn)


@router.delete("/dashboard/categories/{category_id}", response_model=CategoryOut)
async def remove_category(current_user: AccountDb = Depends(get_current_active_admin_user),
                          category_id: str = Path(..., title="Category id"),
                          conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=category_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_category: bool = await exists_category_by_id_impl(category_id=category_id, conn=conn)
    if not exists_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Category does not exist.",
        )
    return await remove_category_by_id_impl(category_id=category_id, conn=conn)


@router.post("/dashboard/categories/{category_id}/sub-categories", response_model=CategoryOut)
async def add_sub_category(current_user: AccountDb = Depends(get_current_active_admin_user),
                           category_id: str = Path(..., title="Category id"),
                           req: RequestAddSubCategory = Body(..., title="Category"),
                           conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=category_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_subcategory: bool = await exists_sub_category_by_name_impl(category_id=category_id, name=req.name,
                                                                      conn=conn)
    if exists_subcategory:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Sub-category already exist.",
        )
    exists_category: bool = await exists_category_by_id_impl(category_id=category_id, conn=conn)
    if not exists_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    sub_category_in: SubCategoryIn = SubCategoryIn()
    sub_category_in.id = str(uuid.UUID(bytes=os.urandom(16), version=4))
    sub_category_in.name = req.name
    return await add_sub_category_impl(category_id=category_id, sub_category_in=sub_category_in, conn=conn)


@router.delete("/dashboard/categories/{category_id}/sub-categories/{sub_category_id}")
async def remove_sub_category(current_user: AccountDb = Depends(get_current_active_admin_user),
                              category_id: str = Path(..., title="Category id"),
                              sub_category_id: str = Path(..., title="sub category id"),
                              conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=category_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_subcategory: bool = await exists_sub_category_by_id_impl(sub_category_id=sub_category_id,conn=conn, category_id=category_id)
    if not exists_subcategory:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Sub-category does not exist.",
        )
    exists_category: bool = await exists_category_by_id_impl(category_id=category_id, conn=conn)
    if not exists_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    return await remove_sub_category_impl(category_id=category_id, sub_category_id=sub_category_id, conn=conn)


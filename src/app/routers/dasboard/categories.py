from fastapi import Body, HTTPException
from fastapi import Depends
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST
from typing import List

from src.app.core.generics import is_valid_oid
from src.app.crud.categories import add_category_impl, add_sub_category_impl, remove_category_by_id_impl
from src.app.crud.categories import exists_sub_category_by_name_impl, exists_category_by_name_impl, exists_category_by_id_impl
from src.app.crud.categories import remove_sub_category_impl, exists_sub_category_by_id_impl
from src.app.core.mongodb import AsyncIOMotorClient, get_database
from src.app.models.category import CategoryIn, CategoryOut, SubCategoryIn
from src.app.models.user import UserDb
from src.app.routers.dasboard.dashboard import router
from src.app.routers.users import get_current_active_admin_user
from src.app.validations.categories import RequestAddCategory, RequestAddSubCategory, RequestRemoveCategory, \
    RequestRemoveSubCategory
from src.app.crud.categories import get_all_categories_impl
import uuid
import os
from datetime import datetime


@router.post("/dashboard/categories/add-category", response_model=CategoryOut)
async def add_category(current_user: UserDb = Depends(get_current_active_admin_user),
                       req: RequestAddCategory = Body(..., title="Category"),
                       conn: AsyncIOMotorClient = Depends(get_database)):
    exists_category: bool = await exists_category_by_name_impl(name=req.name, conn=conn)
    if exists_category:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Category already exist.",
        )
    category_in: CategoryIn = CategoryIn()
    category_in.local_id = req.local_id
    category_in.name = req.name
    category_in.sub_categories = []
    utc_now: datetime = datetime.utcnow()
    category_in.created = utc_now
    category_in.modified = utc_now
    category_in.deleted = False
    return await add_category_impl(category_in=category_in, conn=conn)


@router.post("/dashboard/categories/remove-category", response_model=CategoryOut)
async def remove_category(current_user: UserDb = Depends(get_current_active_admin_user),
                          req: RequestRemoveCategory = Body(..., title="Category"),
                          conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=req.category_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_category: bool = await exists_category_by_id_impl(category_id=req.category_id, conn=conn)
    if not exists_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Category does not exist.",
        )
    return await remove_category_by_id_impl(category_id=req.category_id, conn=conn)


@router.post("/dashboard/categories/add-sub-category", response_model=CategoryOut)
async def add_sub_category(current_user: UserDb = Depends(get_current_active_admin_user),
                           req: RequestAddSubCategory = Body(..., title="Category"),
                           conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=req.category_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_subcategory: bool = await exists_sub_category_by_name_impl(category_id=req.category_id, name=req.name,
                                                                      conn=conn)
    if exists_subcategory:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Sub-category already exist.",
        )
    exists_category: bool = await exists_category_by_id_impl(category_id=req.category_id, conn=conn)
    if not exists_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    sub_category_in: SubCategoryIn = SubCategoryIn()
    sub_category_in.id = str(uuid.UUID(bytes=os.urandom(16), version=4))
    sub_category_in.name = req.name
    return await add_sub_category_impl(category_id=req.category_id, sub_category_in=sub_category_in, conn=conn)


@router.post("/dashboard/categories/remove-sub-category")
async def remove_sub_category(current_user: UserDb = Depends(get_current_active_admin_user),
                              req: RequestRemoveSubCategory = Body(..., title="Category"),
                              conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=req.category_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_subcategory: bool = await exists_sub_category_by_id_impl(sub_category_id=req.sub_category_id,conn=conn, category_id=req.category_id)
    if not exists_subcategory:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Sub-category does not exist.",
        )
    exists_category: bool = await exists_category_by_id_impl(category_id=req.category_id, conn=conn)
    if not exists_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    return await remove_sub_category_impl(category_id=req.category_id, sub_category_id=req.sub_category_id, conn=conn)


@router.post("/dashboard/categories/get-all-categories", response_model=List[CategoryOut])
async def get_all_categories(current_user: UserDb = Depends(get_current_active_admin_user),
                             conn: AsyncIOMotorClient = Depends(get_database)):
    return await get_all_categories_impl(conn=conn)

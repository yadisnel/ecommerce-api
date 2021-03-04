from typing import List

from fastapi import Body, HTTPException
from fastapi import Depends, Path
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from core.generics import is_valid_oid
from crud.categories import (
    add_category_impl, add_sub_category_impl, enable_disable_category_by_id_impl,
    exists_category_by_id_include_disabled_impl, exists_sub_category_by_name_include_disabled_impl,
    exists_sub_category_by_id_include_disabled_impl, search_categories_impl,
    exists_category_by_name_include_disabled_impl,
    )
from crud.categories import exists_sub_category_by_name_impl, exists_category_by_name_impl, exists_category_by_id_impl
from crud.categories import enable_disable_sub_category_impl, exists_sub_category_by_id_impl
from core.mongodb import AsyncIOMotorClient, get_database
from crud.countries import exists_country_by_iso_code_include_disabled_impl
from models.categories import CategoryIn, CategoryOut, SubCategoryIn, CategoryDb
from models.accounts import AccountDb
from routers.dasboard.dashboard import router
from routers.accounts import get_current_active_admin_user
from erequests.categories import (
    RequestAddCategory, RequestAddSubCategory, RequestEnableDisableSubCategory,
    RequestFilterCategories, RequestEnableDisableCategory,
    )
import uuid
import os


@router.post("/dashboard/categories/", response_model=CategoryDb)
async def add_category(current_user: AccountDb = Depends(get_current_active_admin_user),
                       e_request: RequestAddCategory = Body(..., title="Category"),
                       conn: AsyncIOMotorClient = Depends(get_database)):
    exists_category: bool = await exists_category_by_name_include_disabled_impl(name=e_request.name,
                                                                                conn=conn)
    if exists_category:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Category already exist.",
            )
    e_request.country_iso_code = e_request.country_iso_code.upper()
    exists_country: bool = await exists_country_by_iso_code_include_disabled_impl(
        country_iso_code=e_request.country_iso_code, conn=conn)
    if not exists_country:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Country code not supported.",
            )
    return await add_category_impl(e_request=e_request,
                                   conn=conn)


@router.delete("/dashboard/categories/{category_id}", response_model=CategoryDb)
async def enable_disable_category(current_user: AccountDb = Depends(get_current_active_admin_user),
                                  category_id: str = Path(..., title="Category id"),
                                  e_request: RequestEnableDisableCategory = Body(..., title="Category is enabled"),
                                  conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=category_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
            )
    exists_category: bool = await exists_category_by_id_include_disabled_impl(category_id=category_id, conn=conn)
    if not exists_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Category does not exist.",
            )
    return await enable_disable_category_by_id_impl(e_request=e_request,
                                                    category_id=category_id,
                                                    conn=conn)


@router.post("/dashboard/categories/{category_id}/sub-categories", response_model=CategoryDb)
async def add_sub_category(current_user: AccountDb = Depends(get_current_active_admin_user),
                           category_id: str = Path(..., title="Category id"),
                           e_request: RequestAddSubCategory = Body(..., title="Category"),
                           conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=category_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
            )
    exists_subcategory: bool = await exists_sub_category_by_name_include_disabled_impl(category_id=category_id,
                                                                                       name=e_request.name,
                                                                                       conn=conn)
    if exists_subcategory:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Sub-category already exist.",
            )
    exists_category: bool = await exists_category_by_id_include_disabled_impl(category_id=category_id,
                                                                              conn=conn)
    if not exists_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
            )
    return await add_sub_category_impl(e_request=e_request,
                                       category_id=category_id,
                                       conn=conn)


@router.delete("/dashboard/categories/{category_id}/sub-categories/{sub_category_id}",  response_model=CategoryDb)
async def enable_disable_sub_category(current_user: AccountDb = Depends(get_current_active_admin_user),
                                      category_id: str = Path(..., title="Category id"),
                                      sub_category_id: str = Path(..., title="sub category id"),
                                      e_request: RequestEnableDisableSubCategory = Body(...,
                                                                                        title="Sub category is "
                                                                                              "enabled"),
                                      conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=category_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
            )
    exists_subcategory: bool = await exists_sub_category_by_id_include_disabled_impl(sub_category_id=sub_category_id,
                                                                                     category_id=category_id,
                                                                                     conn=conn)
    if not exists_subcategory:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Sub-category does not exist.",
            )
    exists_category: bool = await exists_category_by_id_include_disabled_impl(category_id=category_id, conn=conn)
    if not exists_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
            )
    return await enable_disable_sub_category_impl(e_request=e_request,
                                                  category_id=category_id,
                                                  sub_category_id=sub_category_id,
                                                  conn=conn)


@router.post("/dashboard/categories/search", response_model=List[CategoryDb])
async def search_categories(filter_categories: RequestFilterCategories,
                            current_user: AccountDb = Depends(get_current_active_admin_user),
                            conn: AsyncIOMotorClient = Depends(get_database)):
    filter_categories.country_iso_code = filter_categories.country_iso_code.upper()
    exists_country: bool = await exists_country_by_iso_code_include_disabled_impl(
        country_iso_code=filter_categories.country_iso_code,
        conn=conn)
    if not exists_country:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Country does not exist.",
            )
    return await search_categories_impl(conn=conn, filter_categories=filter_categories)

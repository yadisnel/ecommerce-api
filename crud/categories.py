import os
import uuid
from typing import List

import pymongo
from bson import ObjectId

from core.config import ecommerce_database_name, categories_collection_name
from core.mongodb import AsyncIOMotorClient
from crud.countries import get_country_by_iso_code_include_disabled_impl
from erequests.categories import (
    RequestAddCategory,
    RequestEnableDisableSubCategory,
    RequestFilterCategories, RequestEnableDisableCategory, RequestAddSubCategory,
    )
from erequests.zones import RequestFilterZones
from models.categories import (
    CategoryIn, SubCategoryIn, SyncCategoriesOut, CategoryDb,
    SubCategoryDb,
    )
from datetime import datetime
from erequests.sync import RequestSync


async def add_category_impl(e_request: RequestAddCategory,
                            conn: AsyncIOMotorClient) -> CategoryDb:
    country = await get_country_by_iso_code_include_disabled_impl(country_iso_code=e_request.country_iso_code,
                                                                  conn=conn)
    category_in: CategoryIn = CategoryIn()
    category_in.name = e_request.name
    category_in.order_n = e_request.order_n
    category_in.sub_categories = []
    utc_now: datetime = datetime.utcnow()
    category_in.created = utc_now
    category_in.modified = utc_now
    category_in.country_iso_code = e_request.country_iso_code
    category_in.enabled = country.enabled
    row = await conn[ecommerce_database_name][categories_collection_name].insert_one(category_in.dict())
    return await get_category_by_id_impl(category_id=str(row.inserted_id), conn=conn)


async def get_category_by_id_impl(category_id: str, conn: AsyncIOMotorClient) -> CategoryDb:
    query = {"_id": ObjectId(category_id), "enabled": True}
    row = await conn[ecommerce_database_name][categories_collection_name].find_one(query)
    if row:
        category_db = CategoryDb(**row)
        category_db.id = str(row['_id'])
        return category_db


async def get_category_by_id_include_disabled_impl(category_id: str, conn: AsyncIOMotorClient) -> CategoryDb:
    query = {"_id": ObjectId(category_id)}
    row = await conn[ecommerce_database_name][categories_collection_name].find_one(query)
    if row:
        category_db = CategoryDb(**row)
        category_db.id = str(row['_id'])
        return category_db


async def get_category_by_name_impl(name: str, conn: AsyncIOMotorClient) -> CategoryDb:
    query = {"name": name, "enabled": True}
    row = await conn[ecommerce_database_name][categories_collection_name].find_one(query)
    if row:
        category_db = CategoryDb(**row)
        category_db.id = str(row['_id'])
        return category_db


async def enable_disable_category_by_id_impl(e_request: RequestEnableDisableCategory,
                                             category_id: str,
                                             conn: AsyncIOMotorClient):
    query = {'$set': {"enabled": e_request.enabled, "modified": datetime.utcnow()}}
    await conn[ecommerce_database_name][categories_collection_name].update_one({"_id": ObjectId(category_id)}, query)
    e_request_sub: RequestEnableDisableSubCategory = RequestEnableDisableSubCategory(enabled=e_request.enabled)
    await enable_disable_sub_categories_impl(e_request=e_request_sub,category_id=category_id,conn=conn)
    return await get_category_by_id_include_disabled_impl(category_id=category_id, conn=conn)


async def exists_category_by_name_impl(name: str, conn: AsyncIOMotorClient) -> bool:
    query = {"name": name, "enabled": True}
    count: int = await conn[ecommerce_database_name][categories_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_category_by_name_include_disabled_impl(name: str, conn: AsyncIOMotorClient) -> bool:
    query = {"name": name}
    count: int = await conn[ecommerce_database_name][categories_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_category_by_id_impl(category_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(category_id), "enabled": True}
    count: int = await conn[ecommerce_database_name][categories_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_category_by_id_include_disabled_impl(category_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(category_id)}
    count: int = await conn[ecommerce_database_name][categories_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def add_sub_category_impl(e_request: RequestAddSubCategory,
                                category_id: str,
                                conn: AsyncIOMotorClient) -> CategoryDb:
    category = await get_category_by_id_include_disabled_impl(category_id=category_id, conn=conn)
    sub_category_in: SubCategoryIn = SubCategoryIn()
    sub_category_in.id = str(uuid.UUID(bytes=os.urandom(16), version=4))
    sub_category_in.name = e_request.name
    sub_category_in.enabled = category.enabled
    query = {"$push": {"sub_categories": sub_category_in.dict()}, "$set": {"modified": datetime.utcnow()}}
    await conn[ecommerce_database_name][categories_collection_name].update_one({"_id": ObjectId(category_id)}, query)
    return await get_category_by_id_include_disabled_impl(category_id=category_id, conn=conn)


async def enable_disable_sub_category_impl(e_request: RequestEnableDisableSubCategory,
                                           category_id: str, sub_category_id: str,
                                           conn: AsyncIOMotorClient) -> CategoryDb:
    query = {"$set": {"sub_categories.$.enabled": e_request.enabled, "modified": datetime.utcnow()}}

    await conn[ecommerce_database_name][categories_collection_name].update_one({"_id": ObjectId(category_id),"sub_categories.id": sub_category_id}, query)
    return await get_category_by_id_include_disabled_impl(category_id=category_id, conn=conn)


async def enable_disable_sub_categories_impl(e_request: RequestEnableDisableSubCategory,
                                           category_id: str,
                                           conn: AsyncIOMotorClient) -> CategoryDb:
    query = {'$set': {"sub_categories.$[].enabled": e_request.enabled, "modified": datetime.utcnow()}}
    await conn[ecommerce_database_name][categories_collection_name].update_one({"_id": ObjectId(category_id)}, query)
    return await get_category_by_id_include_disabled_impl(category_id=category_id, conn=conn)


async def exists_sub_category_by_name_impl(category_id: str, name: str, conn: AsyncIOMotorClient) -> bool:
    query = {"sub_categories.name": name, "_id": ObjectId(category_id), "enabled": True}
    count: int = await conn[ecommerce_database_name][categories_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_sub_category_by_name_include_disabled_impl(category_id: str, name: str,
                                                            conn: AsyncIOMotorClient) -> bool:
    query = {"sub_categories.name": name, "_id": ObjectId(category_id)}
    count: int = await conn[ecommerce_database_name][categories_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_sub_category_by_id_impl(category_id: str, sub_category_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(category_id), "sub_categories.id": sub_category_id, "sub_categories.enabled": True}
    count: int = await conn[ecommerce_database_name][categories_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_sub_category_by_id_include_disabled_impl(category_id: str, sub_category_id: str,
                                                          conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(category_id), "sub_categories.id": sub_category_id}
    count: int = await conn[ecommerce_database_name][categories_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def get_sub_category_by_id_impl(category_id: str, sub_category_id: str,
                                      conn: AsyncIOMotorClient) -> SubCategoryDb:
    query = {
        "_id": ObjectId(category_id),
        "sub_categories.id": sub_category_id,
        "sub_categories.enabled": True,
        "sub_categories": {"$elemMatch": {"id": sub_category_id}}
        }
    row = await conn[ecommerce_database_name][categories_collection_name].find_one(query)
    if row:
        sub_category_db = SubCategoryDb(**row['sub_categories'][0])
        sub_category_db.id = str(row['_id'])
        return sub_category_db


async def get_sub_category_by_id_include_disabled_impl(category_id: str, sub_category_id: str,
                                                       conn: AsyncIOMotorClient) -> SubCategoryDb:
    query = {
        "_id": ObjectId(category_id),
        "sub_categories.id": sub_category_id,
        "sub_categories": {"$elemMatch": {"id": sub_category_id}}
        }
    row = await conn[ecommerce_database_name][categories_collection_name].find_one(query)
    if row:
        sub_category_db = SubCategoryDb(**row['sub_categories'][0])
        sub_category_db.id = str(row['_id'])
        return sub_category_db


async def search_categories_impl(filter_categories: RequestFilterCategories, conn: AsyncIOMotorClient) -> List[CategoryDb]:
    categories: List[CategoryDb] = []
    or_array = []
    if filter_categories.load_disabled:
        or_array.append({'enabled': False})
    if filter_categories.load_enabled:
        or_array.append({'enabled': True})
    query = {"country_iso_code": filter_categories.country_iso_code, '$or': or_array}
    rows = conn[ecommerce_database_name][categories_collection_name].find(query)
    async for row in rows:
        category_db = CategoryDb(**row)
        category_db.id = str(row['_id'])
        categories.append(category_db)
    return categories


async def sync_categories_impl(req: RequestSync, conn: AsyncIOMotorClient) -> SyncCategoriesOut:
    sync_category_out: SyncCategoriesOut = SyncCategoriesOut()
    sync_category_out.is_last_offset = False
    categories: List[CategoryDb] = []
    query_10 = {"modified": {"$gt": req.last_offset}}
    if req.is_db_new:
        query_10 = {"modified": {"$gt": req.last_offset}, "enabled": True}
    rows_10 = conn[ecommerce_database_name][categories_collection_name].find(query_10).limit(10)
    async for row in rows_10:
        category_db = CategoryDb(**row)
        category_db.id = str(row['_id'])
        categories.append(category_db)
    sync_category_out.categories = categories
    if len(categories) > 0:
        query_last_change = {"modified": {"$gt": req.last_offset}}
        if req.is_db_new:
            query_last_change = {"modified": {"$gt": req.last_offset}, "enabled": True}
        rows_last_change = conn[ecommerce_database_name][categories_collection_name].find(query_last_change).sort(
            "modified", pymongo.DESCENDING).limit(1)
        async for row in rows_last_change:
            category_out = CategoryDb(**row)
            category_out.id = str(row['_id'])
            if category_out.id == categories[len(categories) - 1].id:
                sync_category_out.is_last_offset = True
    if len(categories) == 0:
        sync_category_out.is_last_offset = True
    return sync_category_out


async def get_categories_offset_impl(conn: AsyncIOMotorClient) -> datetime:
    offset: datetime = datetime.utcnow()
    query_last_change = {}
    rows_last_change = conn[ecommerce_database_name][categories_collection_name].find(query_last_change).sort(
        "modified",
        pymongo.DESCENDING).limit(
        1)
    async for row in rows_last_change:
        category_db = CategoryDb(**row)
        category_db.id = str(row['_id'])
        offset = category_db.modified
    return offset

from typing import List

import pymongo
from bson import ObjectId

from src.app.core.config import dtododb_database_name, categories_collection_name
from src.app.core.mongodb import AsyncIOMotorClient
from src.app.models.category import CategoryIn, CategoryOut, SubCategoryIn, SubCategoryOut, SyncCategoriesOut
from datetime import datetime
from src.app.validations.sync import RequestSync



async def add_category_impl(category_in: CategoryIn, conn: AsyncIOMotorClient) -> CategoryOut:
    row = await conn[dtododb_database_name][categories_collection_name].insert_one(category_in.dict())
    return await get_category_by_id_impl(category_id=str(row.inserted_id), conn=conn)


async def get_category_by_id_impl(category_id: str, conn: AsyncIOMotorClient) -> CategoryOut:
    query = {"_id": ObjectId(category_id), "deleted": False}
    row = await conn[dtododb_database_name][categories_collection_name].find_one(query)
    if row:
        category_out = CategoryOut(**row)
        category_out.id = str(row['_id'])
        return category_out


async def get_category_by_name_impl(name: str, conn: AsyncIOMotorClient) -> CategoryOut:
    query = {"name": name, "deleted": False}
    row = await conn[dtododb_database_name][categories_collection_name].find_one(query)
    if row:
        category_out = CategoryOut(**row)
        category_out.id = str(row['_id'])
        return category_out


async def remove_category_by_id_impl(conn: AsyncIOMotorClient, category_id: str):
    query = {'$set': {"deleted": True, "modified": datetime.utcnow()}, "deleted": False}
    await conn[dtododb_database_name][categories_collection_name].update_one({"_id": ObjectId(category_id)},query)
    return await get_category_by_id_impl(category_id=category_id, conn=conn)


async def exists_category_by_name_impl(name: str, conn: AsyncIOMotorClient) -> bool:
    query = {"name": name, "deleted": False}
    count: int = await conn[dtododb_database_name][categories_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_category_by_id_impl(category_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(category_id), "deleted": False}
    count: int = await conn[dtododb_database_name][categories_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def add_sub_category_impl(category_id: str, sub_category_in: SubCategoryIn, conn: AsyncIOMotorClient) -> CategoryOut:
    query = {"$push": { "sub_categories":sub_category_in.dict()}, "$set": {"modified": datetime.utcnow()}}
    await conn[dtododb_database_name][categories_collection_name].update_one({"_id": ObjectId(category_id)},query)
    return await get_category_by_id_impl(category_id=category_id, conn=conn)


async def remove_sub_category_impl(category_id: str, sub_category_id: str, conn: AsyncIOMotorClient) -> CategoryOut:
    query = {"$pull": { "sub_categories": {"id": sub_category_id}},"$set": {"modified": datetime.utcnow()}}
    await conn[dtododb_database_name][categories_collection_name].update_one({"_id": ObjectId(category_id)},query)
    return await get_category_by_id_impl(category_id=category_id, conn=conn)


async def exists_sub_category_by_name_impl(category_id: str, name: str, conn: AsyncIOMotorClient) -> bool:
    query = {"sub_categories.name": name, "_id": ObjectId(category_id), "deleted": False}
    count: int = await conn[dtododb_database_name][categories_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_sub_category_by_id_impl(category_id: str, sub_category_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"_id":ObjectId(category_id), "sub_categories.id": sub_category_id}
    count: int = await conn[dtododb_database_name][categories_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def get_sub_category_by_id_impl(category_id: str, sub_category_id: str, conn: AsyncIOMotorClient) -> SubCategoryOut:
    query = {"_id":ObjectId(category_id), "sub_categories.id": sub_category_id, "sub_categories": {"$elemMatch": {"id":sub_category_id}}}
    row = await conn[dtododb_database_name][categories_collection_name].find_one(query)
    if row:
        sub_category_out = SubCategoryOut(**row['sub_categories'][0])
        sub_category_out.id = str(row['_id'])
        return sub_category_out


async def get_all_categories_impl(conn: AsyncIOMotorClient) -> List[CategoryOut]:
    categories: List[CategoryOut] = []
    query = {"deleted": False}
    rows = conn[dtododb_database_name][categories_collection_name].find(query)
    async for row in rows:
        category_out = CategoryOut(**row)
        category_out.id = str(row['_id'])
        categories.append(category_out)
    return categories


async def sync_categories_impl(req: RequestSync, conn: AsyncIOMotorClient) -> SyncCategoriesOut:
    sync_category_out: SyncCategoriesOut = SyncCategoriesOut()
    sync_category_out.is_last_offset = False
    categories: List[CategoryOut] = []
    query_10 = {"modified": {"$gt": req.last_offset}}
    if req.is_db_new:
        query_10 = {"modified": {"$gt": req.last_offset}, "deleted": False}
    rows_10 = conn[dtododb_database_name][categories_collection_name].find(query_10).limit(10)
    async for row in rows_10:
        category_out = CategoryOut(**row)
        category_out.id = str(row['_id'])
        categories.append(category_out)
    sync_category_out.categories = categories
    if len(categories) > 0:
        query_last_change = {"modified": {"$gt": req.last_offset}}
        if req.is_db_new:
            query_last_change = {"modified": {"$gt": req.last_offset}, "deleted": False}
        rows_last_change = conn[dtododb_database_name][categories_collection_name].find(query_last_change).sort(
            "modified", pymongo.DESCENDING).limit(1)
        async for row in rows_last_change:
            province_out = CategoryOut(**row)
            province_out.id = str(row['_id'])
            if province_out.id == categories[len(categories) - 1].id:
                sync_category_out.is_last_offset = True
    if len(categories) == 0:
        sync_category_out.is_last_offset = True
    return sync_category_out


async def get_categories_offset_impl(conn: AsyncIOMotorClient) -> datetime:
    offset: datetime = datetime.utcnow()
    query_last_change = {}
    rows_last_change = conn[dtododb_database_name][categories_collection_name].find(query_last_change).sort("modified",
                                                                                                           pymongo.DESCENDING).limit(
        1)
    async for row in rows_last_change:
        category_out = CategoryOut(**row)
        category_out.id = str(row['_id'])
        offset = category_out.modified
    return offset
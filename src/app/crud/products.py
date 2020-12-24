import json
import math
from typing import List, Dict

import pymongo
from bson import ObjectId

from src.app.core.config import dtododb_database_name, products_collection_name, product_favorites_collection_name
from src.app.core.emqx import get_user_topic
from src.app.core.emqx import mqtt_client
from src.app.core.mongodb import AsyncIOMotorClient
from src.app.models.image import Image
from src.app.models.location import Location
from src.app.models.pagination_params import PaginationParams
from src.app.models.product import ProductFavoritedIn, ProductFavoritedOut
from src.app.models.product import ProductIn, ProductDb, ProductOut
from src.app.validations.paginations import RequestPagination
from src.app.validations.paginations import RequestPaginationParams
from src.app.validations.products import RequestSearchProducts


async def add_product_impl(user_id: str, product_in: ProductIn, conn: AsyncIOMotorClient) -> ProductDb:
    row = await conn[dtododb_database_name][products_collection_name].insert_one(product_in.dict())
    mqtt_client.publish(topic=get_user_topic(user_id=user_id), payload=json.dumps(product_in.dict()), qos=2)
    return await get_product_by_id_impl(user_id=user_id, product_id=str(row.inserted_id), conn=conn)


async def get_product_by_id_impl(user_id: str, product_id: str, conn: AsyncIOMotorClient) -> ProductDb:
    query = {"_id": ObjectId(product_id), "user_id": user_id}
    row = await conn[dtododb_database_name][products_collection_name].find_one(query)
    if row:
        product_db = ProductDb(**row)
        product_db.id = str(row['_id'])
        return product_db


async def exists_product_by_id_impl(user_id: str, product_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(product_id), "user_id": user_id, "deleted": False}
    count: int = await conn[dtododb_database_name][products_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def update_complete_product_by_id(user_id: str, product_id: str, product_in: ProductIn,
                                        conn: AsyncIOMotorClient) -> ProductDb:
    query = {'$set': product_in.dict()}
    await conn[dtododb_database_name][products_collection_name].update_one(
        {"_id": ObjectId(product_id), "user_id": user_id}, query)
    mqtt_client.publish(topic=get_user_topic(user_id=user_id), payload=json.dumps(product_in.dict()), qos=2)
    return await get_product_by_id_impl(user_id=user_id, product_id=product_id, conn=conn)


async def update_all_products_shop_info_impl(user_id: str, location: Location, province_id: str, province_name: str,
                                             conn: AsyncIOMotorClient):
    query = {'$set': {"location": location.dict(), "province_id": province_id, "province_name": province_name}}
    await conn[dtododb_database_name][products_collection_name].update_many({"user_id": user_id}, query)


async def remove_product_by_id_impl(conn: AsyncIOMotorClient, user_id: str, product_id: str):
    query = {"_id": ObjectId(product_id), "user_id": user_id}
    await conn[dtododb_database_name][products_collection_name].delete_one(query)


async def add_image_to_product_impl(user_id: str, product_id: str, image_in: Image,
                                    conn: AsyncIOMotorClient) -> ProductDb:
    query = {"$push": {"images": image_in.dict()}}
    await conn[dtododb_database_name][products_collection_name].update_one(
        {"_id": ObjectId(product_id), "user_id": user_id}, query)
    return await get_product_by_id_impl(user_id=user_id, product_id=product_id, conn=conn)


async def remove_image_from_product_impl(user_id: str, product_id: str, image_id: str,
                                         conn: AsyncIOMotorClient) -> ProductDb:
    query = {"$pull": {"images": {"id": image_id}}}
    await conn[dtododb_database_name][products_collection_name].update_one(
        {"_id": ObjectId(product_id), "user_id": user_id}, query)
    return await get_product_by_id_impl(user_id=user_id, product_id=user_id, conn=conn)


async def exists_image_in_product_impl(user_id: str, product_id: str, image_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {'$and': [{'_id': ObjectId(product_id)}, {"user_id": user_id}, {"images.id": image_id}]}
    count: int = await conn[dtododb_database_name][products_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def search_own_products_pagination_params_impl(request_pagination_params: RequestPaginationParams, user_id: str,
                                                     conn: AsyncIOMotorClient) -> PaginationParams:
    and_array = [{"user_id": user_id}]
    query = {'$and': and_array}
    count: float = await conn[dtododb_database_name][products_collection_name].count_documents(query)
    pages: int = 0
    elements: float = request_pagination_params.elements
    if count > 0 and elements > 0:
        pages = math.ceil(count / elements)
    pagination_params: PaginationParams = PaginationParams()
    pagination_params.elements = request_pagination_params.elements
    pagination_params.total = count
    pagination_params.pages = pages
    return pagination_params


async def search_own_products_impl(user_id: str, pagination: RequestPagination, conn: AsyncIOMotorClient) -> List[
    ProductOut]:
    resp: List[ProductOut] = []
    and_array = [{"user_id": user_id}]
    query = {'$and': and_array}
    rows = conn[dtododb_database_name][products_collection_name].find(query).sort("created", pymongo.DESCENDING).skip(
        (pagination.page - 1) * pagination.elements).limit(pagination.elements)
    async for row in rows:
        product_own: ProductOut = ProductOut(**row)
        product_own.id = str(row['_id'])
        resp.append(product_own)
    return resp


async def exists_product_favorited_impl(user_id: str, product_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"product_id": product_id, "user_id": user_id}
    count: int = await conn[dtododb_database_name][product_favorites_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def set_product_favorited_impl(product_favorited: ProductFavoritedIn,
                                     conn: AsyncIOMotorClient) -> ProductFavoritedOut:
    exists_favorited: bool = await exists_product_favorited_impl(user_id=product_favorited.user_id,
                                                                 product_id=product_favorited.product_id, conn=conn)
    if exists_favorited:
        query = {'$set': {"favorited": product_favorited.favorited}}
        await conn[dtododb_database_name][product_favorites_collection_name].update_one(
            {"product_id": product_favorited.product_id, "user_id": product_favorited.user_id}, query)
    else:
        await conn[dtododb_database_name][product_favorites_collection_name].insert_one(product_favorited.dict())
    return await get_product_favorited_impl(user_id=product_favorited.user_id, product_id=product_favorited.product_id,
                                            conn=conn)


async def get_product_favorited_impl(user_id: str, product_id: str, conn: AsyncIOMotorClient) -> ProductFavoritedOut:
    query = {"user_id": user_id, "product_id": product_id}
    row = await conn[dtododb_database_name][products_collection_name].find_one(query)
    if row:
        product_favorited = ProductFavoritedOut(**row)
        product_favorited.id = str(row['_id'])
        return product_favorited


async def get_user_products_favorited_in_array(user_id: str, products_ids: List[str], conn: AsyncIOMotorClient) -> Dict:
    resp: Dict = {}
    and_array = [{"user_id": user_id}, {"product_id": {"$in": products_ids}}]
    query = {'$and': and_array}
    rows = conn[dtododb_database_name][products_collection_name].find(query)
    async for row in rows:
        resp[row['product_id']] = row['favorited']
    return resp


async def search_products_pagination_params_impl(request_pagination_params: RequestPaginationParams,
                                                 filter: RequestSearchProducts,
                                                 user_id: str,
                                                 conn: AsyncIOMotorClient) -> PaginationParams:
    and_array = []
    and_enabled = False
    if filter is not None:
        if filter.province_id is not None:
            and_array.append({"province_id": filter.province_id})
            and_enabled = True
        if filter.category_id is not None:
            and_array.append({"category_id": filter.category_id})
            and_enabled = True
        if filter.sub_category_id is not None:
            and_array.append({"sub_category_id": filter.sub_category_id})
            and_enabled = True
        if filter.min_price is not None:
            and_array.append({"min_price": {"$gte": filter.min_price}})
            and_enabled = True
        if filter.max_price is not None:
            and_array.append({"min_price": {"$lte": filter.max_price}})
            and_enabled = True
        if filter.near is not None:
            and_array.append({"location": {
                "$centerSphere": [[filter.near.coordinates, filter.near.coordinates[1]], filter.near_radius / 6378.1]}})
            and_enabled = True
        if filter.text_search is not None:
            and_array.append({"$text": {"$search": filter.text_search}})
            and_array.append({"tscore": {"$meta": "textScore"}})
            and_enabled = True
    if and_enabled:
        query = {'$and': and_array}
    else:
        query = {}
    count: float = await conn[dtododb_database_name][products_collection_name].count_documents(query)
    pages: int = 0
    elements: float = request_pagination_params.elements
    if count > 0 and elements > 0:
        pages = math.ceil(count / elements)
    pagination_params: PaginationParams = PaginationParams()
    pagination_params.elements = request_pagination_params.elements
    pagination_params.total = count
    pagination_params.pages = pages
    return pagination_params


async def search_products_impl(user_id: str, pagination: RequestPagination, filter: RequestSearchProducts,
                               conn: AsyncIOMotorClient) -> List[ProductOut]:
    resp: List[ProductOut] = []
    and_array = []
    sort_array = [("score", pymongo.DESCENDING)]
    and_enabled = False
    if filter is not None:
        if filter.province_id is not None:
            and_array.append({"province_id": filter.province_id})
            and_enabled = True
        if filter.category_id is not None:
            and_array.append({"category_id": filter.category_id})
            and_enabled = True
        if filter.sub_category_id is not None:
            and_array.append({"sub_category_id": filter.sub_category_id})
            and_enabled = True
        if filter.min_price is not None:
            and_array.append({"min_price": {"$gte": filter.min_price}})
            and_enabled = True
        if filter.max_price is not None:
            and_array.append({"min_price": {"$lte": filter.max_price}})
            and_enabled = True
        if filter.near is not None:
            and_array.append({"location": {
                "$centerSphere": [[filter.near.coordinates, filter.near.coordinates[1]], filter.near_radius / 6378.1]}})
            and_enabled = True
        if filter.text_search is not None:
            and_array.append({"$text": {"$search": filter.text_search}})
            and_array.append({"tscore": {"$meta": "textScore"}})
            and_enabled = True
    if and_enabled:
        query = {'$and': and_array}
    else:
        query = {}
    if filter is not None and filter.text_search is not None:
        sort_array.append(({"tscore": {"$meta": "textScore"}}, pymongo.DESCENDING))
    rows = conn[dtododb_database_name][products_collection_name].find(query).sort(sort_array).skip(
        (pagination.page - 1) * pagination.elements).limit(pagination.elements)
    products_ids: List[str] = []
    async for row in rows:
        product_out: ProductOut = ProductOut(**row)
        product_out.id = str(row['_id'])
        products_ids.append(product_out.id)
        resp.append(product_out)
    dict_favorited: Dict = await get_user_products_favorited_in_array(user_id=user_id, products_ids=products_ids,
                                                                      conn=conn)
    for product_out in resp:
        if product_out.id in dict_favorited:
            product_out.favorited = dict_favorited[product_out.id]
        else:
            product_out.favorited = False
    return resp

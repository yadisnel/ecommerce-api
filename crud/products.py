import json
import math
from typing import List, Dict

import pymongo
from bson import ObjectId

from core.config import ecommerce_database_name, products_collection_name, product_favorites_collection_name
from core.emqx import get_user_topic
from core.emqx import mqtt_client
from core.mongodb import AsyncIOMotorClient
from models.images import ImageDb
from models.pagination_params import PaginationParams
from models.products import ProductFavoriteIn, ProductFavoriteOut
from models.products import ProductIn, ProductDb, ProductOut
from erequests.paginations import RequestPagination
from erequests.paginations import RequestPaginationParams
from erequests.products import RequestSearchProducts
from models.shops import ShopDb


async def add_product_impl(account_id: str, product_in: ProductIn, conn: AsyncIOMotorClient) -> ProductDb:
    row = await conn[ecommerce_database_name][products_collection_name].insert_one(product_in.dict())
    mqtt_client.publish(topic=get_user_topic(account_id=account_id), payload=json.dumps(product_in.dict()), qos=2)
    return await get_product_by_id_impl(account_id=account_id, product_id=str(row.inserted_id), conn=conn)


async def get_product_by_id_impl(account_id: str, product_id: str, conn: AsyncIOMotorClient) -> ProductDb:
    query = {"_id": ObjectId(product_id), "account_id": account_id}
    row = await conn[ecommerce_database_name][products_collection_name].find_one(query)
    if row:
        product_db = ProductDb(**row)
        product_db.id = str(row['_id'])
        return product_db


async def exists_product_by_id_impl(account_id: str, product_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(product_id), "account_id": account_id, "deleted": False}
    count: int = await conn[ecommerce_database_name][products_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def update_complete_product_by_id(account_id: str, product_id: str, product_in: ProductIn,
                                        conn: AsyncIOMotorClient) -> ProductDb:
    query = {'$set': product_in.dict()}
    await conn[ecommerce_database_name][products_collection_name].update_one(
        {"_id": ObjectId(product_id), "account_id": account_id}, query)
    mqtt_client.publish(topic=get_user_topic(account_id=account_id), payload=json.dumps(product_in.dict()), qos=2)
    return await get_product_by_id_impl(account_id=account_id, product_id=product_id, conn=conn)


async def update_all_products_shop_info_impl(shop_db:ShopDb, conn: AsyncIOMotorClient):
    query = {'$set': {"location": shop_db.location, "zone_id": shop_db.zone_id, "zone_name": shop_db.zone_name}}
    await conn[ecommerce_database_name][products_collection_name].update_many({"account_id": shop_db.account_id, "shop_id":shop_db.id}, query)


async def remove_product_by_id_impl(conn: AsyncIOMotorClient, account_id: str, product_id: str):
    query = {"_id": ObjectId(product_id), "account_id": account_id}
    await conn[ecommerce_database_name][products_collection_name].delete_one(query)


async def add_image_to_product_impl(account_id: str, product_id: str, image_in: ImageDb,
                                    conn: AsyncIOMotorClient) -> ProductDb:
    query = {"$push": {"images": image_in.dict()}}
    await conn[ecommerce_database_name][products_collection_name].update_one(
        {"_id": ObjectId(product_id), "account_id": account_id}, query)
    return await get_product_by_id_impl(account_id=account_id, product_id=product_id, conn=conn)


async def remove_image_from_product_impl(account_id: str, product_id: str, image_id: str,
                                         conn: AsyncIOMotorClient) -> ProductDb:
    query = {"$pull": {"images": {"id": image_id}}}
    await conn[ecommerce_database_name][products_collection_name].update_one(
        {"_id": ObjectId(product_id), "account_id": account_id}, query)
    return await get_product_by_id_impl(account_id=account_id, product_id=account_id, conn=conn)


async def exists_image_in_product_impl(account_id: str, product_id: str, image_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {'$and': [{'_id': ObjectId(product_id)}, {"account_id": account_id}, {"images.id": image_id}]}
    count: int = await conn[ecommerce_database_name][products_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_product_favorited_impl(account_id: str, product_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"product_id": product_id, "account_id": account_id}
    count: int = await conn[ecommerce_database_name][product_favorites_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def set_product_favorited_impl(product_favorited: ProductFavoriteIn,
                                     conn: AsyncIOMotorClient) -> ProductFavoriteOut:
    exists_favorited: bool = await exists_product_favorited_impl(account_id=product_favorited.account_id,
                                                                 product_id=product_favorited.product_id, conn=conn)
    if exists_favorited:
        query = {'$set': {"favorited": product_favorited.favorite}}
        await conn[ecommerce_database_name][product_favorites_collection_name].update_one(
            {"product_id": product_favorited.product_id, "account_id": product_favorited.account_id}, query)
    else:
        await conn[ecommerce_database_name][product_favorites_collection_name].insert_one(product_favorited.dict())
    return await get_product_favorited_impl(account_id=product_favorited.account_id, product_id=product_favorited.product_id,
                                            conn=conn)


async def get_product_favorited_impl(account_id: str, product_id: str, conn: AsyncIOMotorClient) -> ProductFavoriteOut:
    query = {"account_id": account_id, "product_id": product_id}
    row = await conn[ecommerce_database_name][products_collection_name].find_one(query)
    if row:
        product_favorited = ProductFavoriteOut(**row)
        product_favorited.id = str(row['_id'])
        return product_favorited


async def get_user_products_favorited_in_array(account_id: str, products_ids: List[str], conn: AsyncIOMotorClient) -> Dict:
    resp: Dict = {}
    and_array = [{"account_id": account_id}, {"product_id": {"$in": products_ids}}]
    query = {'$and': and_array}
    rows = conn[ecommerce_database_name][products_collection_name].find(query)
    async for row in rows:
        resp[row['product_id']] = row['favorited']
    return resp


async def search_products_pagination_params_impl(request_pagination_params: RequestPaginationParams,
                                                 filter: RequestSearchProducts,
                                                 account_id: str,
                                                 conn: AsyncIOMotorClient) -> PaginationParams:
    and_array = []
    and_enabled = False
    if filter is not None:
        if filter.zone_id is not None:
            and_array.append({"zone_id": filter.zone_id})
            and_enabled = True
        if filter.own is not None and filter.own:
            and_array.append({"account_id": account_id})
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
    count: float = await conn[ecommerce_database_name][products_collection_name].count_documents(query)
    pages: int = 0
    elements: float = request_pagination_params.elements
    if count > 0 and elements > 0:
        pages = math.ceil(count / elements)
    pagination_params: PaginationParams = PaginationParams()
    pagination_params.elements = request_pagination_params.elements
    pagination_params.total = count
    pagination_params.pages = pages
    return pagination_params


async def search_products_impl(account_id: str, pagination: RequestPagination, filter: RequestSearchProducts,
                               conn: AsyncIOMotorClient) -> List[ProductOut]:
    resp: List[ProductOut] = []
    and_array = []
    sort_array = [("score", pymongo.DESCENDING)]
    and_enabled = False
    if filter is not None:
        if filter.zone_id is not None:
            and_array.append({"zone_id": filter.zone_id})
            and_enabled = True
        if filter.own is not None and filter.own:
            and_array.append({"account_id": account_id})
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
    rows = conn[ecommerce_database_name][products_collection_name].find(query).sort(sort_array).skip(
        (pagination.page - 1) * pagination.elements).limit(pagination.elements)
    products_ids: List[str] = []
    async for row in rows:
        product_out: ProductOut = ProductOut(**row)
        product_out.id = str(row['_id'])
        products_ids.append(product_out.id)
        resp.append(product_out)
    dict_favorited: Dict = await get_user_products_favorited_in_array(account_id=account_id, products_ids=products_ids,
                                                                      conn=conn)
    for product_out in resp:
        if product_out.id in dict_favorited:
            product_out.favorited = dict_favorited[product_out.id]
        else:
            product_out.favorited = False
    return resp

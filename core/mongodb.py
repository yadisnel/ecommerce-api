import logging

import pymongo
from motor.motor_asyncio import AsyncIOMotorClient

from core.config import (
    db_url, max_connections_count, min_conections_count, ecommerce_database_name,
    accounts_collection_name, pending_accounts_collection_name, zones_collection_name, shops_collection_name,
    )
from core.config import countries_collection_name


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


async def get_database() -> AsyncIOMotorClient:
    return db.client


async def connect_to_mongo():
    logging.info("Connecting to mongodb...")
    db.client = AsyncIOMotorClient(str(db_url),
                                   maxPoolSize=max_connections_count,
                                   minPoolSize=min_conections_count)
    conn: AsyncIOMotorClient = await get_database()
    # ---------------------- Create db indexes----------------------------------
    # accounts_collection_name
    await conn[ecommerce_database_name][accounts_collection_name].create_index([('standard_account_info.email', pymongo.ASCENDING)], unique=True)
    # pending_accounts_collection_name
    await conn[ecommerce_database_name][pending_accounts_collection_name].create_index([('email', pymongo.ASCENDING)])
    await conn[ecommerce_database_name][pending_accounts_collection_name].create_index([('security_code', pymongo.ASCENDING)])
    # shops_collection_name
    await conn[ecommerce_database_name][shops_collection_name].create_index([('account_id', pymongo.ASCENDING)])
    await conn[ecommerce_database_name][shops_collection_name].create_index([('name', pymongo.TEXT),('zone_name', pymongo.TEXT),('country_iso_code', pymongo.TEXT)], default_language='english')
    await conn[ecommerce_database_name][shops_collection_name].create_index([('location', pymongo.GEOSPHERE)])
    await conn[ecommerce_database_name][shops_collection_name].create_index([('images.id', pymongo.ASCENDING)])
    await conn[ecommerce_database_name][shops_collection_name].create_index([('zone_id', pymongo.ASCENDING)])
    await conn[ecommerce_database_name][shops_collection_name].create_index([('country_iso_code', pymongo.ASCENDING)])
    # products_collection_name

    # categories_collection_name

    # zones_collection_name
    await conn[ecommerce_database_name][zones_collection_name].create_index([('country_iso_code', pymongo.ASCENDING)])
    # countries_collection_name
    await conn[ecommerce_database_name][countries_collection_name].create_index([('country_iso_code', pymongo.ASCENDING)], unique=True)
    await conn[ecommerce_database_name][countries_collection_name].create_index([('enabled', pymongo.ASCENDING)])
    # product_favorites_collection_name

    # conversations_collection_name

    # messages_collection_name

    # collection.create_index([('field_i_want_to_index', pymongo.TEXT)], name='search_index', default_language='english')
    logging.info("Mongodb Conected！")


async def close_mongo_connection():
    logging.info("Closing mongodb conection...")
    db.client.close()
    logging.info("Mongodb conection closed！")

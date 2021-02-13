import logging

import pymongo
from motor.motor_asyncio import AsyncIOMotorClient

from core.config import db_url, max_connections_count, min_conections_count, ecommerce_database_name, \
    accounts_collection_name, pending_accounts_collection_name


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
    await conn[ecommerce_database_name][accounts_collection_name].create_index([('standard_account_info.email', pymongo.ASCENDING)],unique=True)
    await conn[ecommerce_database_name][pending_accounts_collection_name].create_index([('email', pymongo.ASCENDING)])
    await conn[ecommerce_database_name][pending_accounts_collection_name].create_index([('security_code', pymongo.ASCENDING)])


    #collection.create_index([('field_i_want_to_index', pymongo.TEXT)], name='search_index', default_language='english')
    logging.info("Mongodb Conected！")


async def close_mongo_connection():
    logging.info("Closing mongodb conection...")
    db.client.close()
    logging.info("Mongodb conection closed！")

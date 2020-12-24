import logging

from motor.motor_asyncio import AsyncIOMotorClient

from src.app.core.config import db_url, max_connections_count, min_conections_count


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
    logging.info("Mongodb Conected！")


async def close_mongo_connection():
    logging.info("Closing mongodb conection...")
    db.client.close()
    logging.info("Mongodb conection closed！")

from datetime import datetime
from typing import List

import pymongo
from bson import ObjectId

from core.config import ecommerce_database_name, countries_collection_name, PAYLOAD_TYPE_COUNTRY
from core.emqx import get_all_users_topic
from core.emqx import mqtt_client
from core.mongodb import AsyncIOMotorClient
from models.countries import CountryIn, CountryOut
from models.mqtt_payloads import MqttPayload
from models.countries import SyncCountriesOut
from erequests.sync import RequestSync


async def add_country_impl(country_in: CountryIn, conn: AsyncIOMotorClient) -> CountryOut:
    row = await conn[ecommerce_database_name][countries_collection_name].insert_one(country_in.dict())
    country = await get_country_by_id_impl(country_id=str(row.inserted_id), conn=conn)
    mqtt_payload: MqttPayload = MqttPayload()
    mqtt_payload.payload_type = PAYLOAD_TYPE_COUNTRY
    mqtt_payload.payload = country.json()
    mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)
    return country


async def get_country_by_id_impl(country_id: str, conn: AsyncIOMotorClient) -> CountryOut:
    query = {"_id": ObjectId(country_id), "deleted": False}
    row = await conn[ecommerce_database_name][countries_collection_name].find_one(query)
    if row:
        country_out = CountryOut(**row)
        country_out.id = str(row['_id'])
        return country_out


async def remove_country_by_id_impl(conn: AsyncIOMotorClient, country_id: str):
    await conn[ecommerce_database_name][countries_collection_name].update_one({"_id": ObjectId(country_id)},
                                                                              {"$set": {"deleted": True,
                                                                                        "modified": datetime.utcnow()}})
    country = await get_country_by_id_impl(country_id=country_id, conn=conn)
    mqtt_payload: MqttPayload = MqttPayload()
    mqtt_payload.payload_type = PAYLOAD_TYPE_COUNTRY
    mqtt_payload.payload = country.json()
    mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)
    return country


async def exists_country_by_name_impl(name: str,
                                      conn: AsyncIOMotorClient) -> bool:
    query = {"name": name, "deleted": False}
    count: int = await conn[ecommerce_database_name][countries_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_country_by_iso_code_impl(country_iso_code: str,
                                          conn: AsyncIOMotorClient) -> bool:
    query = {"country_iso_code": country_iso_code, "deleted": False}
    count: int = await conn[ecommerce_database_name][countries_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_country_by_id_impl(country_id: str,
                                    conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(country_id), "deleted": False}
    count: int = await conn[ecommerce_database_name][countries_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def update_country_impl(country_id: str,
                              name: str, country_iso_code: str,
                              order_n: int,
                              conn: AsyncIOMotorClient):
    await conn[ecommerce_database_name][countries_collection_name].update_one(
        {"_id": ObjectId(country_id)},
        {"$set":
            {
                "name": name,
                "country_iso_code": country_iso_code,
                "n_order": order_n,
                "modified": datetime.utcnow()
            }
        }
    )
    country = await get_country_by_id_impl(country_id=country_id,
                                           conn=conn)
    mqtt_payload: MqttPayload = MqttPayload()
    mqtt_payload.payload_type = PAYLOAD_TYPE_COUNTRY
    mqtt_payload.payload = country.json()
    mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)
    return country


async def get_all_countries_impl(conn: AsyncIOMotorClient) -> List[CountryOut]:
    countries: List[CountryOut] = []
    query = {}
    rows = conn[ecommerce_database_name][countries_collection_name].find(query)
    async for row in rows:
        country_out = CountryOut(**row)
        country_out.id = str(row['_id'])
        countries.append(country_out)
    return countries


async def sync_countries_impl(req: RequestSync,
                              conn: AsyncIOMotorClient) -> SyncCountriesOut:
    sync_country_out: SyncCountriesOut = SyncCountriesOut()
    sync_country_out.is_last_offset = False
    countries: List[CountryOut] = []
    query_10 = {"modified": {"$gt": req.last_offset}}
    if req.is_db_new:
        query_10 = {"modified": {"$gt": req.last_offset}, "deleted": False}
    rows_10 = conn[ecommerce_database_name][countries_collection_name].find(query_10).limit(10)
    async for row in rows_10:
        country_out = CountryOut(**row)
        country_out.id = str(row['_id'])
        countries.append(country_out)
    sync_country_out.countries = countries
    if len(countries) > 0:
        query_last_change = {"modified": {"$gt": req.last_offset}}
        if req.is_db_new:
            query_last_change = {"modified": {"$gt": req.last_offset}, "deleted": False}
        rows_last_change = conn[ecommerce_database_name][countries_collection_name].find(query_last_change).sort(
            "modified", pymongo.DESCENDING).limit(1)
        async for row in rows_last_change:
            country_out = CountryOut(**row)
            country_out.id = str(row['_id'])
            if country_out.id == countries[len(countries) - 1].id:
                sync_country_out.is_last_offset = True
    if len(countries) == 0:
        sync_country_out.is_last_offset = True
    return sync_country_out


async def get_countries_offset_impl(conn: AsyncIOMotorClient) -> datetime:
    offset: datetime = datetime.utcnow()
    query_last_change = {}
    rows_last_change = conn[ecommerce_database_name][countries_collection_name].find(query_last_change).sort("modified",
                                                                                                             pymongo.DESCENDING).limit(
        1)
    async for row in rows_last_change:
        country_out = CountryOut(**row)
        country_out.id = str(row['_id'])
        offset = country_out.modified
    return offset

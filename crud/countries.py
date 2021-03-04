from datetime import datetime
from typing import List

import pycountry
import pymongo
from bson import ObjectId
from core.config import (
    ecommerce_database_name, countries_collection_name, PAYLOAD_TYPE_COUNTRY, zones_collection_name,
    PAYLOAD_TYPE_ZONE, categories_collection_name,
    )
from core.emqx import get_all_users_topic
from core.emqx import mqtt_client
from core.mongodb import AsyncIOMotorClient
from erequests.countries import RequestAddCountry
from erequests.countries import RequestUpdateCountry
from erequests.countries import RequestFilterCountries
from erequests.countries import RequestEnableDisableCountry
from erequests.zones import RequestFilterZones
from models.countries import CountryIn, CountryOut, CountryDb
from models.mqtt_payloads import MqttPayload
from models.countries import SyncCountriesOut
from erequests.sync import RequestSync
from models.zones import ZoneDb


async def add_country_impl(e_request: RequestAddCountry, conn: AsyncIOMotorClient) -> CountryDb:
    country_in: CountryIn = CountryIn()
    country = pycountry.countries.get(alpha_2=e_request.country_iso_code)
    country_in.name = country.name
    country_in.order_n = e_request.order_n
    country_in.country_iso_code = e_request.country_iso_code
    utc_now: datetime = datetime.utcnow()
    country_in.created = utc_now
    country_in.modified = utc_now
    country_in.enabled = True
    row = await conn[ecommerce_database_name][countries_collection_name].insert_one(country_in.dict())
    country = await get_country_by_id_impl(country_id=str(row.inserted_id), conn=conn)
    mqtt_payload: MqttPayload = MqttPayload()
    mqtt_payload.payload_type = PAYLOAD_TYPE_COUNTRY
    mqtt_payload.payload = country.json()
    mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)
    return country


async def get_country_by_id_with_deleted_impl(country_id: str, conn: AsyncIOMotorClient) -> CountryOut:
    query = {"_id": ObjectId(country_id)}
    row = await conn[ecommerce_database_name][countries_collection_name].find_one(query)
    if row:
        country_out = CountryOut(**row)
        country_out.id = str(row['_id'])
        return country_out


async def get_country_by_id_impl(country_id: str, conn: AsyncIOMotorClient) -> CountryDb:
    query = {"_id": ObjectId(country_id), "enabled": True}
    row = await conn[ecommerce_database_name][countries_collection_name].find_one(query)
    if row:
        country_db = CountryDb(**row)
        country_db.id = str(row['_id'])
        return country_db


async def search_zones_impl(filter_zones: RequestFilterZones, conn: AsyncIOMotorClient) -> List[ZoneDb]:
    zones: List[ZoneDb] = []
    or_array = []
    if filter_zones.load_disabled:
        or_array.append({'enabled': False})
    if filter_zones.load_enabled:
        or_array.append({'enabled': True})
    query = {"country_iso_code": filter_zones.country_iso_code, '$or': or_array}
    rows = conn[ecommerce_database_name][zones_collection_name].find(query)
    async for row in rows:
        zone_db = ZoneDb(**row)
        zone_db.id = str(row['_id'])
        zones.append(zone_db)
    return zones


async def enable_disable_all_zones_by_country_iso_code_impl(enabled: bool,
                                                            country_iso_code: str,
                                                            conn: AsyncIOMotorClient):
    await conn[ecommerce_database_name][zones_collection_name].update_many({"country_iso_code": country_iso_code},
                                                                           {
                                                                               "$set": {
                                                                                   "enabled": enabled,
                                                                                   "modified": datetime.utcnow()
                                                                                   }
                                                                               })
    filter_zones: RequestFilterZones = RequestFilterZones(load_enabled=True,
                                                          load_disabled=True,
                                                          country_iso_code=country_iso_code)

    zones = await search_zones_impl(filter_zones=filter_zones, conn=conn)
    for zone in zones:
        mqtt_payload: MqttPayload = MqttPayload()
        mqtt_payload.payload_type = PAYLOAD_TYPE_ZONE
        mqtt_payload.payload = zone.json()
        mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)


async def enable_disable_all_categories_by_country_iso_code_impl(enabled: bool,
                                                                 country_iso_code: str,
                                                                 conn: AsyncIOMotorClient):
    query = {'$set': {"enabled": enabled,"sub_categories.$[].enabled": enabled, "modified": datetime.utcnow()}}
    await conn[ecommerce_database_name][categories_collection_name].update_many({"country_iso_code": country_iso_code}, query)


async def enable_disable_country_by_id_impl(e_request: RequestEnableDisableCountry,
                                            conn: AsyncIOMotorClient, country_id: str):
    await conn[ecommerce_database_name][countries_collection_name].update_one(
        {"_id": ObjectId(country_id)},
        {
            "$set":
                {
                    "enabled": e_request.enabled,
                    "modified": datetime.utcnow()
                    }
            }
        )
    country = await get_country_by_id_with_deleted_impl(country_id=country_id, conn=conn)
    mqtt_payload: MqttPayload = MqttPayload()
    mqtt_payload.payload_type = PAYLOAD_TYPE_COUNTRY
    mqtt_payload.payload = country.json()
    mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)
    await enable_disable_all_zones_by_country_iso_code_impl(enabled=e_request.enabled,
                                                            country_iso_code=country.country_iso_code,
                                                            conn=conn)
    await enable_disable_all_categories_by_country_iso_code_impl(enabled=e_request.enabled,
                                                                 country_iso_code=country.country_iso_code,
                                                                 conn=conn)
    return country


async def exists_country_by_name_impl(name: str,
                                      conn: AsyncIOMotorClient) -> bool:
    query = {"name": name, "enabled": True}
    count: int = await conn[ecommerce_database_name][countries_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_country_by_iso_code_impl(country_iso_code: str,
                                          conn: AsyncIOMotorClient) -> bool:
    query = {"country_iso_code": country_iso_code, "enabled": True}
    count: int = await conn[ecommerce_database_name][countries_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_country_by_iso_code_include_disabled_impl(country_iso_code: str,
                                                           conn: AsyncIOMotorClient) -> bool:
    query = {"country_iso_code": country_iso_code}
    count: int = await conn[ecommerce_database_name][countries_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def get_country_by_iso_code_include_disabled_impl(country_iso_code: str,
                                                        conn: AsyncIOMotorClient) -> CountryDb:
    query = {"country_iso_code": country_iso_code}
    row = await conn[ecommerce_database_name][countries_collection_name].find_one(query)
    if row:
        country_db = CountryDb(**row)
        country_db.id = str(row['_id'])
        return country_db


async def get_country_by_iso_code_impl(country_iso_code: str,
                                                        conn: AsyncIOMotorClient) -> CountryDb:
    query = {"country_iso_code": country_iso_code, "enabled": True}
    row = await conn[ecommerce_database_name][countries_collection_name].find_one(query)
    if row:
        country_db = CountryDb(**row)
        country_db.id = str(row['_id'])
        return country_db


async def exists_country_by_id_impl(country_id: str,
                                    conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(country_id), "enabled": True}
    count: int = await conn[ecommerce_database_name][countries_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_country_by_id_include_disabled_impl(country_id: str,
                                                     conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(country_id)}
    count: int = await conn[ecommerce_database_name][countries_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def update_country_impl(country_id: str,
                              e_request: RequestUpdateCountry,
                              conn: AsyncIOMotorClient):
    await conn[ecommerce_database_name][countries_collection_name].update_one(
        {"_id": ObjectId(country_id)},
        {
            "$set":
                {
                    "name": e_request.name,
                    "n_order": e_request.order_n,
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


async def search_countries_impl(filter_countries: RequestFilterCountries, conn: AsyncIOMotorClient) -> List[CountryDb]:
    countries: List[CountryDb] = []
    or_array = []
    if filter_countries.load_enabled:
        or_array.append({'enabled': True})
    if filter_countries.load_disabled:
        or_array.append({'enabled': False})
    query = {'$or': or_array}
    rows = conn[ecommerce_database_name][countries_collection_name].find(query)
    async for row in rows:
        country_db = CountryDb(**row)
        country_db.id = str(row['_id'])
        countries.append(country_db)
    return countries


async def sync_countries_impl(req: RequestSync,
                              conn: AsyncIOMotorClient) -> SyncCountriesOut:
    sync_country_out: SyncCountriesOut = SyncCountriesOut()
    sync_country_out.is_last_offset = False
    countries: List[CountryOut] = []
    query_10 = {"modified": {"$gt": req.last_offset}}
    if req.is_db_new:
        query_10 = {"modified": {"$gt": req.last_offset}, "Enabled": True}
    rows_10 = conn[ecommerce_database_name][countries_collection_name].find(query_10).limit(10)
    async for row in rows_10:
        country_out = CountryOut(**row)
        country_out.id = str(row['_id'])
        countries.append(country_out)
    sync_country_out.countries = countries
    if len(countries) > 0:
        query_last_change = {"modified": {"$gt": req.last_offset}}
        if req.is_db_new:
            query_last_change = {"modified": {"$gt": req.last_offset}, "enabled": True}
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

from datetime import datetime
from typing import List

import pymongo
from bson import ObjectId

from core.config import ecommerce_database_name, zones_collection_name, PAYLOAD_TYPE_ZONE
from core.emqx import get_all_users_topic
from core.emqx import mqtt_client
from core.mongodb import AsyncIOMotorClient
from erequests.zones import RequestUpdateZone, RequestFilterZones
from models.mqtt_payloads import MqttPayload
from models.zones import ZoneIn, ZoneOut, ZoneDb
from models.zones import SyncZonesOut
from erequests.sync import RequestSync


async def add_zone_impl(zone_in: ZoneIn, conn: AsyncIOMotorClient) -> ZoneDb:
    row = await conn[ecommerce_database_name][zones_collection_name].insert_one(zone_in.dict())
    zone_db = await get_zone_by_id_impl(zone_id=str(row.inserted_id), conn=conn)
    mqtt_payload: MqttPayload = MqttPayload()
    mqtt_payload.payload_type = PAYLOAD_TYPE_ZONE
    mqtt_payload.payload = ZoneOut(**zone_db.dict()).json()
    mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)
    return zone_db


async def get_zone_by_id_impl(zone_id: str, conn: AsyncIOMotorClient) -> ZoneDb:
    query = {"_id": ObjectId(zone_id), "deleted": False}
    row = await conn[ecommerce_database_name][zones_collection_name].find_one(query)
    if row:
        zone_db = ZoneDb(**row)
        zone_db.id = str(row['_id'])
        return zone_db


async def get_zone_by_id_without_deleted_impl(zone_id: str, conn: AsyncIOMotorClient) -> ZoneDb:
    query = {"_id": ObjectId(zone_id)}
    row = await conn[ecommerce_database_name][zones_collection_name].find_one(query)
    if row:
        zone_db = ZoneDb(**row)
        zone_db.id = str(row['_id'])
        return zone_db


async def remove_zone_by_id_impl(conn: AsyncIOMotorClient, zone_id: str):
    await conn[ecommerce_database_name][zones_collection_name].update_one({"_id": ObjectId(zone_id)},
                                                                          {"$set": {"deleted": True,
                                                                                    "modified": datetime.utcnow()}})
    zone = await get_zone_by_id_without_deleted_impl(zone_id=zone_id, conn=conn)
    mqtt_payload: MqttPayload = MqttPayload()
    mqtt_payload.payload_type = PAYLOAD_TYPE_ZONE
    mqtt_payload.payload = zone.json()
    mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)
    return zone


async def exists_zone_by_name_and_country_iso_code_impl(name: str, country_iso_code: str, conn: AsyncIOMotorClient) -> bool:
    query = {"name": name,"country_iso_code": country_iso_code, "deleted": False}
    count: int = await conn[ecommerce_database_name][zones_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_zone_by_id_impl(zone_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(zone_id), "deleted": False}
    count: int = await conn[ecommerce_database_name][zones_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_zone_without_deleted_impl(zone_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(zone_id)}
    count: int = await conn[ecommerce_database_name][zones_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def update_zone_impl(e_request: RequestUpdateZone, zone_id: str, conn: AsyncIOMotorClient):
    await conn[ecommerce_database_name][zones_collection_name].update_one(
        {
            "_id": ObjectId(zone_id)
        },
        {
            "$set":
                {
                    "name": e_request.name,
                    "n_order": e_request.order_n,
                    "deleted": e_request.deleted,
                    "modified": datetime.utcnow()
                }
        }
    )
    zone = await get_zone_by_id_without_deleted_impl(zone_id=zone_id, conn=conn)
    mqtt_payload: MqttPayload = MqttPayload()
    mqtt_payload.payload_type = PAYLOAD_TYPE_ZONE
    mqtt_payload.payload = zone.json()
    mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)
    return zone


async def get_all_zones_impl(filter_zones: RequestFilterZones, conn: AsyncIOMotorClient) -> List[ZoneDb]:
    zones: List[ZoneDb] = []
    or_array = []
    if filter_zones.load_not_deleted or (not filter_zones.load_not_deleted and not filter_zones.load_deleted):
        or_array.append({'deleted': False})
    if filter_zones.load_deleted:
        or_array.append({'deleted': True})
    query = {"country_iso_code": filter_zones.country_iso_code, '$or': or_array}
    rows = conn[ecommerce_database_name][zones_collection_name].find(query)
    async for row in rows:
        zone_db = ZoneDb(**row)
        zone_db.id = str(row['_id'])
        zones.append(zone_db)
    return zones


async def sync_zones_impl(req: RequestSync, conn: AsyncIOMotorClient) -> SyncZonesOut:
    sync_zone_out: SyncZonesOut = SyncZonesOut()
    sync_zone_out.is_last_offset = False
    zones: List[ZoneOut] = []
    query_10 = {"modified": {"$gt": req.last_offset}}
    if req.is_db_new:
        query_10 = {"modified": {"$gt": req.last_offset}, "deleted": False}
    rows_10 = conn[ecommerce_database_name][zones_collection_name].find(query_10).limit(10)
    async for row in rows_10:
        zone_out = ZoneOut(**row)
        zone_out.id = str(row['_id'])
        zones.append(zone_out)
    sync_zone_out.zones = zones
    if len(zones) > 0:
        query_last_change = {"modified": {"$gt": req.last_offset}}
        if req.is_db_new:
            query_last_change = {"modified": {"$gt": req.last_offset}, "deleted": False}
        rows_last_change = conn[ecommerce_database_name][zones_collection_name].find(query_last_change).sort(
            "modified", pymongo.DESCENDING).limit(1)
        async for row in rows_last_change:
            zone_out = ZoneOut(**row)
            zone_out.id = str(row['_id'])
            if zone_out.id == zones[len(zones) - 1].id:
                sync_zone_out.is_last_offset = True
    if len(zones) == 0:
        sync_zone_out.is_last_offset = True
    return sync_zone_out


async def get_zones_offset_impl(conn: AsyncIOMotorClient) -> datetime:
    offset: datetime = datetime.utcnow()
    query_last_change = {}
    rows_last_change = conn[ecommerce_database_name][zones_collection_name].find(query_last_change).sort("modified",
                                                                                                         pymongo.DESCENDING).limit(
        1)
    async for row in rows_last_change:
        zone_out = ZoneOut(**row)
        zone_out.id = str(row['_id'])
        offset = zone_out.modified
    return offset

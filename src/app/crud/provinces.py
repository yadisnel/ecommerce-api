from datetime import datetime
from typing import List

import pymongo
from bson import ObjectId

from src.app.core.config import dtododb_database_name, provinces_collection_name, PAYLOAD_TYPE_PROVINCE
from src.app.core.emqx import get_all_users_topic
from src.app.core.emqx import mqtt_client
from src.app.core.mongodb import AsyncIOMotorClient
from src.app.models.mqtt_payload import MqttPayload
from src.app.models.province import ProvinceIn, ProvinceOut
from src.app.models.province import SyncProvincesOut
from src.app.validations.sync import RequestSync


async def add_province_impl(province_in: ProvinceIn, conn: AsyncIOMotorClient) -> ProvinceOut:
    row = await conn[dtododb_database_name][provinces_collection_name].insert_one(province_in.dict())
    province = await get_province_by_id_impl(province_id=str(row.inserted_id), conn=conn)
    mqtt_payload: MqttPayload = MqttPayload()
    mqtt_payload.payload_type = PAYLOAD_TYPE_PROVINCE
    mqtt_payload.payload = province.json()
    mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)
    return province


async def get_province_by_id_impl(province_id: str, conn: AsyncIOMotorClient) -> ProvinceOut:
    query = {"_id": ObjectId(province_id), "deleted": False}
    row = await conn[dtododb_database_name][provinces_collection_name].find_one(query)
    if row:
        province_out = ProvinceOut(**row)
        province_out.id = str(row['_id'])
        return province_out


async def remove_province_by_id_impl(conn: AsyncIOMotorClient, province_id: str):
    await conn[dtododb_database_name][provinces_collection_name].update_one({"_id": ObjectId(province_id)},
                                                                            {"$set": {"deleted": True,
                                                                                      "modified": datetime.utcnow()}})
    province = await get_province_by_id_impl(province_id=province_id, conn=conn)
    mqtt_payload: MqttPayload = MqttPayload()
    mqtt_payload.payload_type = PAYLOAD_TYPE_PROVINCE
    mqtt_payload.payload = province.json()
    mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)
    return province


async def exists_province_by_name_impl(name: str, conn: AsyncIOMotorClient) -> bool:
    query = {"name": name, "deleted": False}
    count: int = await conn[dtododb_database_name][provinces_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_province_by_id_impl(province_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(province_id), "deleted": False}
    count: int = await conn[dtododb_database_name][provinces_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def update_province_name_impl(province_id: str, name: str, order: int, conn: AsyncIOMotorClient):
    await conn[dtododb_database_name][provinces_collection_name].update_one({"_id": ObjectId(province_id)},
                                                                            {"$set": {"name": name,
                                                                                      "n_order": order,
                                                                                      "modified": datetime.utcnow()}})
    province = await get_province_by_id_impl(province_id=province_id, conn=conn)
    mqtt_payload: MqttPayload = MqttPayload()
    mqtt_payload.payload_type = PAYLOAD_TYPE_PROVINCE
    mqtt_payload.payload = province.json()
    mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)
    return province


async def get_all_provinces_impl(conn: AsyncIOMotorClient) -> List[ProvinceOut]:
    provinces: List[ProvinceOut] = []
    query = {}
    rows = conn[dtododb_database_name][provinces_collection_name].find(query)
    async for row in rows:
        province_out = ProvinceOut(**row)
        province_out.id = str(row['_id'])
        provinces.append(province_out)
    return provinces


async def sync_provinces_impl(req: RequestSync, conn: AsyncIOMotorClient) -> SyncProvincesOut:
    sync_province_out: SyncProvincesOut = SyncProvincesOut()
    sync_province_out.is_last_offset = False
    provinces: List[ProvinceOut] = []
    query_10 = {"modified": {"$gt": req.last_offset}}
    if req.is_db_new:
        query_10 = {"modified": {"$gt": req.last_offset}, "deleted": False}
    rows_10 = conn[dtododb_database_name][provinces_collection_name].find(query_10).limit(10)
    async for row in rows_10:
        province_out = ProvinceOut(**row)
        province_out.id = str(row['_id'])
        provinces.append(province_out)
    sync_province_out.provinces = provinces
    if len(provinces) > 0:
        query_last_change = {"modified": {"$gt": req.last_offset}}
        if req.is_db_new:
            query_last_change = {"modified": {"$gt": req.last_offset}, "deleted": False}
        rows_last_change = conn[dtododb_database_name][provinces_collection_name].find(query_last_change).sort(
            "modified", pymongo.DESCENDING).limit(1)
        async for row in rows_last_change:
            province_out = ProvinceOut(**row)
            province_out.id = str(row['_id'])
            if province_out.id == provinces[len(provinces) - 1].id:
                sync_province_out.is_last_offset = True
    if len(provinces) == 0:
        sync_province_out.is_last_offset = True
    return sync_province_out


async def get_provinces_offset_impl(conn: AsyncIOMotorClient) -> datetime:
    offset: datetime = datetime.utcnow()
    query_last_change = {}
    rows_last_change = conn[dtododb_database_name][provinces_collection_name].find(query_last_change).sort("modified",
                                                                                                           pymongo.DESCENDING).limit(
        1)
    async for row in rows_last_change:
        province_out = ProvinceOut(**row)
        province_out.id = str(row['_id'])
        offset = province_out.modified
    return offset

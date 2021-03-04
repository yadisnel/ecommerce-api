from bson import ObjectId
from core.config import bucket_config, PAYLOAD_TYPE_ZONE
from core.config import ecommerce_database_name, shops_collection_name
from core.emqx import get_all_users_topic, mqtt_client
from core.mongodb import AsyncIOMotorClient
from core.s3 import delete_object_on_s3
from crud.zones import get_zone_by_id_impl
from erequests.shops import RequestAddShop, RequestUpdateShop
from models.images import ImageDb
from models.mqtt_payloads import MqttPayload
from models.shops import ShopDb, ShopIn, ShopOut
from models.zones import ZoneDb


async def add_shop_impl(e_request: RequestAddShop, account_id: str, conn: AsyncIOMotorClient) -> ShopDb:
    zone_db: ZoneDb = await get_zone_by_id_impl(zone_id=e_request.zone_id, conn=conn)
    shop_in: ShopIn = ShopIn()
    shop_in.name = e_request.name
    shop_in.account_id = account_id
    shop_in.images = []
    if e_request.location is not None:
        shop_in.location = []
        shop_in.location.append(e_request.location.long)
        shop_in.location.append(e_request.location.lat)
    else:
        shop_in.location = None
    shop_in.zone_id = zone_db.id
    shop_in.zone_name = zone_db.name
    shop_in.country_iso_code = zone_db.country_iso_code
    shop_in.enabled = True
    row = await conn[ecommerce_database_name][shops_collection_name].insert_one(shop_in.dict())
    shop_db = await get_shop_by_id_impl(shop_id=str(row.inserted_id), conn=conn)
    mqtt_payload: MqttPayload = MqttPayload()
    mqtt_payload.payload_type = PAYLOAD_TYPE_ZONE
    mqtt_payload.payload = ShopOut(**zone_db.dict()).json()
    mqtt_client.publish(topic=get_all_users_topic(), payload=mqtt_payload.json(), qos=2)
    return shop_db


async def delete_shop_by_id_impl(conn: AsyncIOMotorClient, shop_id: str):
    await conn[ecommerce_database_name][shops_collection_name].delete_one({"_id": ObjectId(shop_id)})


async def update_shop_by_id(shop_id: str, e_request: RequestUpdateShop, conn: AsyncIOMotorClient) -> ShopDb:
    zone_out: ZoneDb = await get_zone_by_id_impl(zone_id=e_request.zone_id, conn=conn)
    shop_db: ShopDb = await get_shop_by_id_impl(shop_id=shop_id, conn=conn)
    shop_in: ShopIn = ShopIn(**shop_db.dict())
    shop_in.name = e_request.name
    shop_in.zone_id = e_request.zone_id
    shop_in.zone_name = zone_out.name
    # db.restaurants.find({
    #                         'address.coord':
    #                             {
    #                                 '$near': [50, 50],
    #                                 '$minDistance': 10,
    #                                 '$maxDistance': 100
    #                                 }
    #                         }).count()
    if e_request.location is not None:
        shop_in.location = []
        shop_in.location.append(e_request.location.long)
        shop_in.location.append(e_request.location.lat)
    else:
        shop_in.location = None
    await conn[ecommerce_database_name][shops_collection_name].update_one({"_id": ObjectId(shop_id)},
                                                                          {"$set": shop_in.dict()})
    return await get_shop_by_id_impl(shop_id=shop_id, conn=conn)


async def get_shop_by_id_impl(shop_id: str, conn: AsyncIOMotorClient) -> ShopDb:
    row = await conn[ecommerce_database_name][shops_collection_name].find_one({"_id": ObjectId(shop_id)})
    if row:
        shop = ShopDb(**row)
        shop.id = str(row['_id'])
        return shop


async def add_image_to_shop_impl(shop_id: str, image_in: ImageDb, conn: AsyncIOMotorClient) -> ShopDb:
    query = {"$push": {"images": image_in.dict()}}
    await conn[ecommerce_database_name][shops_collection_name].update_one({"_id": ObjectId(shop_id)}, query)
    return await get_shop_by_id_impl(shop_id=shop_id, conn=conn)


async def remove_image_from_shop_impl(shop_id: str, image_id: str, conn: AsyncIOMotorClient) -> ShopDb:
    query = {"$pull": {"images": {"id": image_id}}}
    shop_db: ShopDb = await get_shop_by_id_impl(shop_id=shop_id, conn=conn)
    for image in shop_db.images:
        if image.id == image_id:
            delete_object_on_s3(bucket=bucket_config.name(), key=image.original_key, region_name=bucket_config.region())
            delete_object_on_s3(bucket=bucket_config.name(), key=image.thumb_key, region_name=bucket_config.region())
    await conn[ecommerce_database_name][shops_collection_name].update_one({"_id": ObjectId(shop_id)}, query)
    return await get_shop_by_id_impl(shop_id=shop_id, conn=conn)


async def remove_all_images_from_shop_impl(shop: ShopDb, conn: AsyncIOMotorClient) -> ShopDb:
    for image in shop.images:
        delete_object_on_s3(bucket=bucket_config.name(), key=image.original_key, region_name=bucket_config.region())
        delete_object_on_s3(bucket=bucket_config.name(), key=image.thumb_key, region_name=bucket_config.region())
    query = {"$set": {"shop.images": []}}
    await conn[ecommerce_database_name][shops_collection_name].update_one({"_id": ObjectId(shop.id)}, query)
    return await get_shop_by_id_impl(shop_id=shop.id, conn=conn)


async def exists_image_in_shop_by_id_impl(shop_id: str, image_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {{'_id': ObjectId(shop_id)}, {"images.id": image_id}}
    count: int = await conn[ecommerce_database_name][shops_collection_name].count_documents(query)
    if count > 0:
        return True
    return False


async def exists_shop_by_id_impl(shop_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {"_id": ObjectId(shop_id), "enabled": True}
    count: int = await conn[ecommerce_database_name][shops_collection_name].count_documents(query)
    if count > 0:
        return True
    return False

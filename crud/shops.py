from bson import ObjectId

from core.config import bucket_config
from core.config import ecommerce_database_name, shops_collection_name
from core.mongodb import AsyncIOMotorClient
from core.s3 import delete_object_on_s3
from models.images import ImageDb
from models.shops import ShopOut, ShopIn


async def delete_shop_by_id_impl(conn: AsyncIOMotorClient, shop_id: str):
    await conn[ecommerce_database_name][shops_collection_name].delete_one({"_id": ObjectId(shop_id)})


async def update_complete_shop_by_id(shop_id: str, shop_in: ShopIn, conn: AsyncIOMotorClient) -> ShopOut:
    await conn[ecommerce_database_name][shops_collection_name].update_one({"_id": ObjectId(shop_id)},
                                                                          {"$set": {"shop": shop_in.dict()}})
    return await get_shop_by_id_impl(shop_id=shop_id, conn=conn)


async def get_shop_by_id_impl(shop_id: str, conn: AsyncIOMotorClient) -> ShopOut:
    row = await conn[ecommerce_database_name][shops_collection_name].find_one({"_id": ObjectId(shop_id)})
    if row:
        shop = ShopOut(**row)
        shop.id = str(row['_id'])
        return shop


async def add_image_to_shop_impl(shop_id: str, image_in: ImageDb, conn: AsyncIOMotorClient) -> ShopOut:
    query = {"$push": {"images": image_in.dict()}}
    await conn[ecommerce_database_name][shops_collection_name].update_one({"_id": ObjectId(shop_id)}, query)
    return await get_shop_by_id_impl(shop_id=shop_id, conn=conn)


async def remove_image_from_shop_impl(shop_id: str, image_id: str, conn: AsyncIOMotorClient) -> ShopOut:
    query = {"$pull": {"images": {"id": image_id}}}
    # TODO remove image from s3
    await conn[ecommerce_database_name][shops_collection_name].update_one({"_id": ObjectId(shop_id)}, query)
    return await get_shop_by_id_impl(shop_id=shop_id, conn=conn)


async def remove_all_images_from_shop_impl(shop: ShopOut, conn: AsyncIOMotorClient) -> ShopOut:
    for image in shop.images:
        delete_object_on_s3(bucket=bucket_config.name(), key=image.original_key, region_name=bucket_config.region())
        delete_object_on_s3(bucket=bucket_config.name(), key=image.thumb_key, region_name=bucket_config.region())
    query = {"$set": {"shop.images": []}}
    await conn[ecommerce_database_name][shops_collection_name].update_one({"_id": ObjectId(shop.id)}, query)
    return await get_shop_by_id_impl(shop_id=shop.id, conn=conn)


async def exists_image_in_shop_by_id_impl(shop_id: str, image_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {'$and': [{'_id': ObjectId(shop_id)}, {"images.id": image_id}]}
    count: int = await conn[ecommerce_database_name][shops_collection_name].count_documents(query)
    if count > 0:
        return True
    return False

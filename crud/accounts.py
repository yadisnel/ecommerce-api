from bson import ObjectId

from core.config import bucket_config
from core.config import ecommerce_database_name, accounts_collection_name
from core.mongodb import AsyncIOMotorClient
from core.s3 import delete_object_on_s3
from models.images import Image
from models.shops import ShopIn
from models.accounts import AccountDb, AccountIn


async def add_user_impl(conn: AsyncIOMotorClient, account_in: AccountIn) -> AccountDb:
    row = await conn[ecommerce_database_name][accounts_collection_name].insert_one(account_in.dict())
    return await get_user_by_id_impl(user_id=str(row.inserted_id), conn=conn)


async def get_user_by_id_impl(user_id: str, conn: AsyncIOMotorClient) -> AccountDb:
    row = await conn[ecommerce_database_name][accounts_collection_name].find_one({"_id": ObjectId(user_id)})
    if row:
        user = AccountDb(**row)
        user.id = str(row['_id'])
        return user


async def get_user_by_facebook_id_impl(facebook_id: str, conn: AsyncIOMotorClient) -> AccountDb:
    row = await conn[ecommerce_database_name][accounts_collection_name].find_one({"facebook_id": facebook_id})
    if row:
        user = AccountDb(**row)
        user.id = str(row['_id'])
        return user


async def delete_user_by_id_impl(conn: AsyncIOMotorClient, user_id: str):
    await conn[ecommerce_database_name][accounts_collection_name].delete_one({"_id": ObjectId(user_id)})


async def update_complete_user_by_id(conn: AsyncIOMotorClient, user_id: str, user_in: AccountIn) -> AccountDb:
    await conn[ecommerce_database_name][accounts_collection_name].update_one({"_id": ObjectId(user_id)},
                                                                             {'$set': user_in.dict()})
    return await get_user_by_id_impl(user_id=user_id, conn=conn)


async def update_user_token_by_user_id_impl(conn: AsyncIOMotorClient, user_id: str, token: bytes) -> AccountDb:
    await conn[ecommerce_database_name][accounts_collection_name].update_one({"_id": ObjectId(user_id)},
                                                                             {'$set': {"token": token}})
    return await get_user_by_id_impl(user_id=user_id, conn=conn)


async def update_user_facebook_token_by_facebook_id_impl(conn: AsyncIOMotorClient, facebook_id: str,
                                                         facebook_token: bytes) -> AccountDb:
    await conn[ecommerce_database_name][accounts_collection_name].update_one({"facebook_id": facebook_id},
                                                                             {'$set': {"facebook_token": facebook_token}})
    return await get_user_by_facebook_id_impl(facebook_id=facebook_id, conn=conn)


async def update_complete_shop_by_user_id(user_id: str, shop_in: ShopIn, conn: AsyncIOMotorClient):
    user_db: AccountDb = await get_user_by_id_impl(user_id=user_id, conn=conn)
    if user_db is not None:
        user_db.shop = shop_in
        await conn[ecommerce_database_name][accounts_collection_name].update_one({"_id": ObjectId(user_id)},
                                                                                 {"$set": {"shop": shop_in.dict()}})
        return await get_user_by_id_impl(user_id=user_id, conn=conn)


async def add_image_to_shop_impl(user_id: str, image_in: Image, conn: AsyncIOMotorClient) -> AccountDb:
    query = {"$push": {"shop.images": image_in.dict()}}
    await conn[ecommerce_database_name][accounts_collection_name].update_one({"_id": ObjectId(user_id)}, query)
    return await get_user_by_id_impl(user_id=user_id, conn=conn)


async def update_user_avatar_impl(user_id: str, image_in: Image, conn: AsyncIOMotorClient) -> AccountDb:
    query = {"$set": {"picture": image_in.dict()}}
    await conn[ecommerce_database_name][accounts_collection_name].update_one({"_id": ObjectId(user_id)}, query)
    return await get_user_by_id_impl(user_id=user_id, conn=conn)


async def remove_image_from_shop_impl(user_id: str, image_id: str, conn: AsyncIOMotorClient) -> AccountDb:
    query = {"$pull": {"shop.images": {"id": image_id}}}
    await conn[ecommerce_database_name][accounts_collection_name].update_one({"_id": ObjectId(user_id)}, query)
    return await get_user_by_id_impl(user_id=user_id, conn=conn)


async def remove_all_images_from_shop_impl(current_user: AccountDb, conn: AsyncIOMotorClient) -> AccountDb:
    for image in current_user.shop.images:
        delete_object_on_s3(bucket=bucket_config.name(), key=image.original_key, region_name=bucket_config.region())
        delete_object_on_s3(bucket=bucket_config.name(), key=image.thumb_key, region_name=bucket_config.region())
    query = {"$set": {"shop.images": []}}
    await conn[ecommerce_database_name][accounts_collection_name].update_one({"_id": ObjectId(current_user.id)}, query)
    return await get_user_by_id_impl(user_id=current_user.id, conn=conn)


async def exists_image_in_shop_by_id_impl(user_id: str, image_id: str, conn: AsyncIOMotorClient) -> bool:
    query = {'$and': [{'_id': ObjectId(user_id)}, {"shop.images.id": image_id}]}
    count: int = await conn[ecommerce_database_name][accounts_collection_name].count_documents(query)
    if count > 0:
        return True
    return False

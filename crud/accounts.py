from bson import ObjectId
from core.config import ecommerce_database_name, accounts_collection_name
from core.mongodb import AsyncIOMotorClient
from models.images import Image
from models.accounts import AccountDb, AccountIn


async def add_account_impl(conn: AsyncIOMotorClient, account_in: AccountIn) -> AccountDb:
    row = await conn[ecommerce_database_name][accounts_collection_name].insert_one(account_in.dict())
    return await get_account_by_id_impl(account_id=str(row.inserted_id), conn=conn)


async def get_account_by_id_impl(account_id: str, conn: AsyncIOMotorClient) -> AccountDb:
    row = await conn[ecommerce_database_name][accounts_collection_name].find_one({"_id": ObjectId(account_id)})
    if row:
        account = AccountDb(**row)
        account.id = str(row['_id'])
        return account


async def get_account_by_facebook_id_impl(facebook_id: str, conn: AsyncIOMotorClient) -> AccountDb:
    row = await conn[ecommerce_database_name][accounts_collection_name].find_one(
        {"facebook_account_info.id": facebook_id})
    if row:
        account = AccountDb(**row)
        account.id = str(row['_id'])
        return account


async def get_standard_account_by_email_impl(email: str, conn: AsyncIOMotorClient) -> AccountDb:
    row = await conn[ecommerce_database_name][accounts_collection_name].find_one(
        {"standard_account_info.email": email})
    if row:
        account = AccountDb(**row)
        account.id = str(row['_id'])
        return account


async def delete_account_by_id_impl(conn: AsyncIOMotorClient, account_id: str):
    await conn[ecommerce_database_name][accounts_collection_name].delete_one({"_id": ObjectId(account_id)})


async def update_complete_account_by_id(conn: AsyncIOMotorClient, account_id: str, account_in: AccountIn) -> AccountDb:
    await conn[ecommerce_database_name][accounts_collection_name].update_one({"_id": ObjectId(account_id)},
                                                                             {'$set': account_in.dict()})
    return await get_account_by_id_impl(account_id=account_id, conn=conn)


async def update_account_facebook_token_by_facebook_id_impl(conn: AsyncIOMotorClient, facebook_id: str,
                                                            facebook_token: bytes) -> AccountDb:
    await conn[ecommerce_database_name][accounts_collection_name].update_one({"facebook_account_info.id": facebook_id},
                                                                             {'$set': {
                                                                                 "facebook_account_info.token": facebook_token}})
    return await get_account_by_facebook_id_impl(facebook_id=facebook_id, conn=conn)


async def update_account_avatar_impl(account_id: str, image_in: Image, conn: AsyncIOMotorClient) -> AccountDb:
    query = {"$set": {"picture": image_in.dict()}}
    await conn[ecommerce_database_name][accounts_collection_name].update_one({"_id": ObjectId(account_id)}, query)
    return await get_account_by_id_impl(account_id=account_id, conn=conn)

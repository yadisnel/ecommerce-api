from bson import ObjectId
from core.config import ecommerce_database_name, pending_accounts_collection_name
from core.mongodb import AsyncIOMotorClient
from core.security import get_password_hash, generate_security_code_for_email
from models.pending_accounts import StandardPendingAccountDB, StandardPendingAccountIn
from datetime import datetime


async def add_standard_pending_account_with_email(conn: AsyncIOMotorClient,
                                                  email: str,
                                                  password: str) -> StandardPendingAccountDB:
    await delete_standard_pending_account_by_email(conn=conn, email=email)
    standard_pending_in = StandardPendingAccountIn()
    standard_pending_in.email = email
    standard_pending_in.hashed_password = get_password_hash(password=password)
    now = datetime.now()
    date = datetime.timestamp(now)
    date = date * 1000
    standard_pending_in.created_at = int(date)
    standard_pending_in.modified_at = int(date)
    standard_pending_in.security_code = generate_security_code_for_email()
    row = await conn[ecommerce_database_name][pending_accounts_collection_name].insert_one(standard_pending_in.dict())
    return await get_pending_account_by_id_impl(account_id=str(row.inserted_id), conn=conn)


async def get_pending_account_by_id_impl(account_id: str,
                                         conn: AsyncIOMotorClient) -> StandardPendingAccountDB:
    row = await conn[ecommerce_database_name][pending_accounts_collection_name].find_one({"_id": ObjectId(account_id)})
    if row:
        account = StandardPendingAccountDB(**row)
        account.id = str(row['_id'])
        return account


async def get_pending_account_by_security_code_impl(security_code: str,
                                                    conn: AsyncIOMotorClient) -> StandardPendingAccountDB:
    row = await conn[ecommerce_database_name][pending_accounts_collection_name].find_one(
        {
            "security_code": security_code
        }
    )
    if row:
        account = StandardPendingAccountDB(**row)
        account.id = str(row['_id'])
        return account


async def get_pending_account_by_email_impl(email: str,
                                            conn: AsyncIOMotorClient) -> StandardPendingAccountDB:
    row = await conn[ecommerce_database_name][pending_accounts_collection_name].find_one(
        {
            "email": email
        }
    )
    if row:
        account = StandardPendingAccountDB(**row)
        account.id = str(row['_id'])
        return account


async def delete_standard_pending_account_by_email(conn: AsyncIOMotorClient, email: str):
    await conn[ecommerce_database_name][pending_accounts_collection_name].delete_many(
        {
            "email": email
        }
    )
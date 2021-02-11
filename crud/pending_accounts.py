from bson import ObjectId
from core.config import ecommerce_database_name, pending_accounts_collection_name
from core.mongodb import AsyncIOMotorClient
from core.security import get_password_hash, generate_security_code_for_email
from erequests.accounts import RequestRegisterAccountWithEmail
from models.pending_accounts import StandardPendingAccountDb, StandardPendingAccountIn
from datetime import datetime


async def add_standard_pending_account_with_email(e_request: RequestRegisterAccountWithEmail,
                                                  conn: AsyncIOMotorClient) -> StandardPendingAccountDb:
    await delete_standard_pending_account_by_email(conn=conn, email=e_request.email)
    standard_pending_in = StandardPendingAccountIn()
    standard_pending_in.email = e_request.email
    standard_pending_in.hashed_password = get_password_hash(password=e_request.password)
    standard_pending_in.country_iso_code = e_request.country_iso_code
    now = datetime.now()
    date = datetime.timestamp(now)
    date = date * 1000
    standard_pending_in.created_at = int(date)
    standard_pending_in.modified_at = int(date)
    standard_pending_in.security_code = generate_security_code_for_email()
    row = await conn[ecommerce_database_name][pending_accounts_collection_name].insert_one(standard_pending_in.dict())
    return await get_pending_account_by_id_impl(account_id=str(row.inserted_id), conn=conn)


async def get_pending_account_by_id_impl(account_id: str,
                                         conn: AsyncIOMotorClient) -> StandardPendingAccountDb:
    row = await conn[ecommerce_database_name][pending_accounts_collection_name].find_one({"_id": ObjectId(account_id)})
    if row:
        account = StandardPendingAccountDb(**row)
        account.id = str(row['_id'])
        return account


async def get_pending_account_by_security_code_impl(security_code: str,
                                                    conn: AsyncIOMotorClient) -> StandardPendingAccountDb:
    row = await conn[ecommerce_database_name][pending_accounts_collection_name].find_one(
        {
            "security_code": security_code
        }
    )
    if row:
        account = StandardPendingAccountDb(**row)
        account.id = str(row['_id'])
        return account


async def get_pending_account_by_email_impl(email: str,
                                            conn: AsyncIOMotorClient) -> StandardPendingAccountDb:
    row = await conn[ecommerce_database_name][pending_accounts_collection_name].find_one(
        {
            "email": email
        }
    )
    if row:
        account = StandardPendingAccountDb(**row)
        account.id = str(row['_id'])
        return account


async def delete_standard_pending_account_by_email(conn: AsyncIOMotorClient, email: str):
    await conn[ecommerce_database_name][pending_accounts_collection_name].delete_many(
        {
            "email": email
        }
    )
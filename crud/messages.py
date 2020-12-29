from core.mongodb import AsyncIOMotorClient
from models.messages import MessageOut, MessageIn
from core.config import ecommerce_database_name, messges_collection_name
from bson import ObjectId
from core.emqx import mqtt_client
from core.emqx import get_user_topic
import json


async def send_message_impl(message_in: MessageIn, conn: AsyncIOMotorClient) -> MessageOut:
    row = await conn[ecommerce_database_name][messges_collection_name].insert_one(message_in.dict())
    mqtt_client.publish(topic=get_user_topic(user_id=message_in.user_owner_id),payload=json.dumps(message_in.dict()),qos=2)
    return await get_message_by_id_impl(message_id=str(row.inserted_id), conn=conn)


async def get_message_by_id_impl(message_id: str, conn: AsyncIOMotorClient) -> MessageOut:
    query = {"_id": ObjectId(message_id)}
    row = await conn[ecommerce_database_name][messges_collection_name].find_one(query)
    if row:
        message_out = MessageOut(**row)
        message_out.id = str(row['_id'])
        return message_out


async def remove_message_by_id_impl(conn: AsyncIOMotorClient, message_id: str):
    query = {"_id": ObjectId(message_id)}
    await conn[ecommerce_database_name][messges_collection_name].delete_one(query)


async def remove_messages_by_conversation_id_impl(conn: AsyncIOMotorClient, conversation_id: str):
    query = {"conversation_id": conversation_id}
    await conn[ecommerce_database_name][messges_collection_name].delete_many(query)


async def remove_messages_by_conversation_and_user_owner_id_impl(conversation_id: str, user_owner_id, conn: AsyncIOMotorClient):
    query = {"conversation_id": conversation_id, "user_owner_id": user_owner_id}
    await conn[ecommerce_database_name][messges_collection_name].delete_many(query)
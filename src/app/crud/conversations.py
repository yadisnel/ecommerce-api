from bson import ObjectId

from src.app.core.config import dtododb_database_name, conversations_collection_name
from src.app.crud.messages import remove_messages_by_conversation_id_impl, \
    remove_messages_by_conversation_and_user_owner_id_impl
from src.app.core.mongodb import AsyncIOMotorClient
from src.app.models.conversation import ConversationIn, ConversationOut


async def add_conversation_impl(conversation_in: ConversationIn, conn: AsyncIOMotorClient) -> ConversationOut:
    row = await conn[dtododb_database_name][conversations_collection_name].insert_one(conversation_in.dict())
    return await get_conversation_by_id_impl(conversation_id=str(row.inserted_id), conn=conn)


async def get_conversation_by_id_impl(conversation_id: str, conn: AsyncIOMotorClient) -> ConversationOut:
    query = {"_id": ObjectId(conversation_id)}
    row = await conn[dtododb_database_name][conversations_collection_name].find_one(query)
    if row:
        conversation_out = ConversationOut(**row)
        conversation_out.id = str(row['_id'])
        return conversation_out


async def get_conversation_between_users_impl(user_id_1: str, user_id_2: str,
                                              conn: AsyncIOMotorClient) -> ConversationOut:
    query = {"$or": [{'$and': [{"user_id_1": user_id_1}, {"user_id_2": user_id_2}]},
                     {'$and': [{"user_id_1": user_id_2}, {"user_id_2": user_id_1}]}]}
    row = await conn[dtododb_database_name][conversations_collection_name].find_one(query)
    if row:
        conversation_out = ConversationOut(**row)
        conversation_out.id = str(row['_id'])
        return conversation_out


async def remove_conversation_by_conversation_id_impl(conn: AsyncIOMotorClient, conversation_id: str):
    query = {"_id": ObjectId(conversation_id)}
    await conn[dtododb_database_name][conversations_collection_name].delete_one(query)


async def update_complete_conversation_by_id(conversation_id: str, conversation_in: ConversationIn,
                                             conn: AsyncIOMotorClient) -> ConversationOut:
    query = {'$set': conversation_in.dict()}
    await conn[dtododb_database_name][conversations_collection_name].update_one({"_id": ObjectId(conversation_id)},
                                                                                query)
    return await get_conversation_by_id_impl(conversation_id=conversation_id, conn=conn)


async def remove_conversation_from_user_impl(user_id_request: str, user_id_2: str, conn: AsyncIOMotorClient):
    conversation: ConversationOut = await get_conversation_between_users_impl(user_id_1=user_id_request,
                                                                              user_id_2=user_id_2, conn=conn)
    if conversation is not None:
        if conversation.user_id_1 == user_id_request:
            if conversation.user_id_2_out:
                await remove_messages_by_conversation_id_impl(conversation_id=conversation.id, conn=conn)
                await remove_conversation_by_conversation_id_impl(conversation_id=conversation.id, conn=conn)
            else:
                await remove_messages_by_conversation_and_user_owner_id_impl(conversation_id=conversation.id,
                                                                             user_owner_id=user_id_request, conn=conn)
                conversation.user_id_1_out = True
                await update_complete_conversation_by_id(conversation_id=conversation.id,
                                                         conversation_in=ConversationIn(**conversation.dict()),
                                                         conn=conn)
        elif conversation.user_id_2 == user_id_request:
            if conversation.user_id_1_out:
                await remove_messages_by_conversation_id_impl(conversation_id=conversation.id, conn=conn)
                await remove_conversation_by_conversation_id_impl(conversation_id=conversation.id, conn=conn)
            else:
                await remove_messages_by_conversation_and_user_owner_id_impl(conversation_id=conversation.id,
                                                                             user_owner_id=user_id_request, conn=conn)
                conversation.user_id_2_out = True
                await update_complete_conversation_by_id(conversation_id=conversation.id,
                                                         conversation_in=ConversationIn(**conversation.dict()),
                                                         conn=conn)

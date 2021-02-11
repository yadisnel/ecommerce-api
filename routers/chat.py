from datetime import datetime

from fastapi import APIRouter, Path
from fastapi import Body, HTTPException
from fastapi import Depends
from starlette.status import HTTP_400_BAD_REQUEST

from core.generics import is_valid_oid, is_valid_message_body
from crud.conversations import get_conversation_between_users_impl, add_conversation_impl
from crud.messages import send_message_impl
from crud.accounts import get_account_by_id_impl
from core.mongodb import AsyncIOMotorClient, get_database
from models.conversations import ConversationOut, ConversationIn
from models.messages import MessageIn
from models.accounts import AccountDb
from routers.accounts import get_current_active_user
from erequests.messages import RequestSendMessage

router = APIRouter()


@router.post("/chat/messages/")
async def send_chat_message(erequest: RequestSendMessage = Body(..., title="Message"),
                            current_user: AccountDb = Depends(get_current_active_user),
                            conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=erequest.to_user_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid user id.",
        )
    if not is_valid_message_body(body=erequest.body):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid message body",
        )
    to_user: AccountDb = await get_account_by_id_impl(account_id=erequest.to_user_id, conn=conn)
    if to_user is None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid user id.",
        )
    if current_user.id == to_user.id:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="From and to users are equals.",
        )
    conversation: ConversationOut = await get_conversation_between_users_impl(user_id_1=current_user.id,
                                                                              user_id_2=to_user.id, conn=conn)
    if conversation is None:
        conversation_in: ConversationIn = ConversationIn()
        now = datetime.utcnow()
        conversation_in.user_id_1 = current_user.id
        conversation_in.user_id_2 = to_user.id
        conversation_in.user_id_1_out = False
        conversation_in.user_id_2_out = False
        conversation_in.created = now
        conversation_in.modified = now
        conversation = await add_conversation_impl(conversation_in=conversation_in, conn=conn)
    now = datetime.utcnow()
    message_in_from: MessageIn = MessageIn()
    message_in_from.user_owner_id = current_user.id
    message_in_from.conversation_id = conversation.id
    message_in_from.from_user_id = current_user.id
    message_in_from.from_user_name = current_user.name
    message_in_from.to_user_id = to_user.id
    message_in_from.to_user_name = to_user.name
    message_in_from.body = erequest.body
    message_in_from.created = now
    message_in_from.modified = now
    message_in_from.deleted = False
    message_in_to: MessageIn = MessageIn()
    message_in_to.user_owner_id = to_user.id
    message_in_to.conversation_id = conversation.id
    message_in_to.from_user_id = current_user.id
    message_in_to.from_user_name = current_user.name
    message_in_to.to_user_id = to_user.id
    message_in_to.to_user_name = to_user.name
    message_in_to.body = erequest.body
    message_in_to.created = now
    message_in_to.modified = now
    message_in_to.deleted = False
    await send_message_impl(message_in=message_in_from, conn=conn)
    await send_message_impl(message_in=message_in_to, conn=conn)
    return {"success": True}


@router.delete("/chat/messages/{message_id}")
async def remove_chat_message(
        message_id: str = Path(..., title="Message's id"),
        current_user: AccountDb = Depends(get_current_active_user),
        conn: AsyncIOMotorClient = Depends(get_database)):
    # TODO Implement it
    return None

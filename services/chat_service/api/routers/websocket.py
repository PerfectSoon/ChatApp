import json

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict

from api.depends import get_user_from_token
from api.ws_manager import manager

from database.connection import get_db
from database.repositories import ChatMemberRepository, MessageRepository
from services.message import MessageService
from services.chatmember import ChatMemberService


router1 = APIRouter(prefix="/chat")

@router1.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Токен не предоставлен")
        return

    try:
        user = get_user_from_token(token)
        user_id = int(user.get("user_id"))
    except HTTPException:
        await websocket.close(code=4001, reason="Неверный токен")
        return

    member_repo = ChatMemberRepository(db)
    service = ChatMemberService(memrepo=member_repo)
    if not await service.get_user(chat_id, user_id):
        await websocket.close(code=4001, reason="Not a member of this chat")
        return

    await manager.connect(chat_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()

            message_repo = MessageRepository(db)
            service = MessageService(messagerepo=message_repo)
            message = await service.create(
                chat_id=chat_id,
                sender_id=user_id,
                text=data
            )
            message_data = {
                "text": message.text,
                "sender_id": message.sender_id,
                "sent_at": message.sent_at.isoformat()
            }

            await manager.broadcast(chat_id, json.dumps(message_data))

    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)
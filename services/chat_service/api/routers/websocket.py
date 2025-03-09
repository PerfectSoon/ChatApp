from fastapi import APIRouter, HTTPException, Depends, status
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict

from api.depends import get_user_from_token

from database.connection import get_db
from database.repositories import ChatMemberRepository, MessageRepository
from services.message import MessageService


router1 = APIRouter(prefix="/chat")

active_connections = defaultdict(list)

@router1.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await get_user_from_token(token)
        user_id = user.get("user_id")
    except HTTPException:
        await websocket.close(code=1008)
        return

    member_repo = ChatMemberRepository(db)
    if not await member_repo.is_member_exists(chat_id, user_id):
        await websocket.close(code=4001, reason="Not a member of this chat")
        return

    await websocket.accept()
    active_connections[chat_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            message_repo = MessageRepository(db)
            service = MessageService(messagerepo=message_repo)
            await service.create(
                    chat_id=chat_id,
                    sender_id=user_id,
                    text=data
            )

            for connection in active_connections[chat_id]:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_text(f"Message: {data}")

    except WebSocketDisconnect:
        active_connections[chat_id].remove(websocket)
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.schemas import ChatCreate, ChatOut, UserToChat, ChatMemberOut, MessageOut
from database.repositories import ChatRepository, ChatMemberRepository,MessageRepository

from services.chat import ChatService
from services.chatmember import ChatMemberService
from services.message import MessageService

from api.depends import get_user_from_token


router = APIRouter(prefix="/chat")

@router.post("/create", response_model=ChatOut)
async def create_chat(
    chat_data: ChatCreate,
    user: dict = Depends(get_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    owner_id = int(user.get("user_id"))
    print(type(owner_id))
    if not owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id not found in token"
        )
    chat_repo = ChatRepository(db)
    mem_repo = ChatMemberRepository(db)
    chatservice = ChatService(chatrepo=chat_repo,memrepo=mem_repo)
    chat = await chatservice.create_chat(chat_data=chat_data, owner_id=owner_id)

    return chat

@router.get("/all_chats", response_model=List[ChatOut])
async def get_user_chats(
    user: dict = Depends(get_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = int(user.get("user_id"))
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id not found in token"
        )
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chatrepo=chat_repo)
    chats = await chat_service.get_user_chats(user_id=user_id)

    return chats

@router.post("/{chat_id}/add/{user_id}", response_model=ChatMemberOut)
async def add_user_to_chat(
        data: UserToChat,
        db: AsyncSession = Depends(get_db)
):
    try:
        mem_repo = ChatMemberRepository(db)
        service = ChatMemberService(memrepo=mem_repo)
        chat_member = await service.add_user_to_chat(
            chat_id=data.chat_id,
            user_id=int(data.user_id)
        )

        return chat_member
    except HTTPException as e:
        raise e

@router.post("/{chat_id}/delete/{user_id}", response_model=Optional[UserToChat])
async def delete_user_from_chat(
        data: UserToChat,
        db: AsyncSession = Depends(get_db)
):
    try:
        mem_repo = ChatMemberRepository(db)
        service = ChatMemberService(memrepo=mem_repo)
        chat_member = await service.remove_user_from_chat(
            chat_id=data.chat_id,
            user_id=int(data.user_id)
        )

        return chat_member
    except HTTPException as e:
        raise e


@router.post("/delete/{chat_id}", response_model=Optional[ChatOut])
async def delete_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    chat_repo = ChatRepository(db)
    chatservice = ChatService(chatrepo=chat_repo)
    chat = await chatservice.delete_chat(chat_id=chat_id)

    return chat


@router.get("/{chat_id}/messages", response_model=List[MessageOut])
async def get_messages_on_chat(
    chat_id: int,
    current_user: dict = Depends(get_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    user_id = int(current_user.get("user_id"))
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id not found in token"
        )
    mess_repo = MessageRepository(db)
    service = MessageService(messagerepo=mess_repo)
    messages = await service.get_chat_messages(chat_id=chat_id)

    return messages
from dataclasses import dataclass
from typing import List, Optional
from fastapi import HTTPException

from database.repositories import ChatRepository,ChatMemberRepository
from database.models import Chat, ChatMember
from database.schemas import ChatCreate



@dataclass(kw_only=True, frozen=True, slots=True)
class ChatService:
    chatrepo: ChatRepository
    memrepo: Optional[ChatMemberRepository] = None

    async def create_chat(self, chat_data: ChatCreate, owner_id: int) -> Chat:
        chat = Chat(
            type=chat_data.type,
            name=chat_data.name,
            owner_id=int(owner_id)
        )
        created_chat = await self.chatrepo.create(chat=chat)
        if self.memrepo:
            chat_member = ChatMember(chat_id=created_chat.id, user_id=int(owner_id), role="admin")
            await self.memrepo.create(chat_member=chat_member)
        return created_chat


    async def delete_chat(self, chat_id) -> Chat | None:
        return await self.chatrepo.delete(chat_id=chat_id)

    async def get_user_chats(self, user_id: int) -> List[Chat]:
        return await self.chatrepo.get_user_chats(user_id)


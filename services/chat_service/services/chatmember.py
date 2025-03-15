from dataclasses import dataclass
from fastapi import HTTPException
from typing import List

from database.repositories import ChatMemberRepository
from database.schemas import ChatCreate
from database.models import ChatMember, Chat

from api.depends import check_user_exists


@dataclass(kw_only=True, frozen=True, slots=True)
class ChatMemberService:
    memrepo: ChatMemberRepository

    async def add_user_to_chat(self, chat_id: int, user_id: int) -> ChatMember:
        chat = await self.memrepo._get_by_id(model=Chat,id=chat_id)
        if not chat:
            raise HTTPException(404, "Chat not found")

        if chat.type == "private":
            members = await self.memrepo.get_chat_members(chat_id)

            if len(members) >= 2:
                raise HTTPException(400, "Private chat can only have 2 members")

        if not await check_user_exists(user_id):
            raise HTTPException(404, "User not found")

        existing_member = await self.memrepo.get_member(chat_id=chat_id, user_id=user_id)
        if existing_member:
            raise HTTPException(400, "User is already a member of this chat")

        chat_member = ChatMember(chat_id=chat_id, user_id=int(user_id), role="member")
        return await self.memrepo.create(chat_member=chat_member)

    async def remove_user_from_chat(self, chat_id: int, user_id: int) :
        chat = await self.memrepo._get_by_id(model=Chat, id=chat_id)
        if not chat:
            raise HTTPException(404, "Chat not found")

        member = await self.memrepo.remove_member(chat_id, user_id)
        if not await check_user_exists(user_id):
            raise HTTPException(404, "User not found")

        if member.role != "member":
            raise HTTPException(403, "Only members can be removed")

        return member

    async def get_user(self, chat_id: int, user_id: int):
            return await self.memrepo.get_member(chat_id, user_id)


from typing import List, Type, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Chat, ChatMember, Message

class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _execute_query(self, query):
        result = await self.session.execute(query)
        return result.scalars().all()

    async def _get_by_id(self, model: Type, id: int):
        return await self.session.get(model, id)

    async def _get_by_composite_key(self, model, **kwargs):
        query = select(model).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def _add(self, entity):
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def _delete(self, entity):
        if entity is None:
            return None
        await self.session.delete(entity)
        await self.session.commit()
        return entity

    async def _commit(self):
        await self.session.commit()


class ChatRepository(BaseRepository):
    async def get_user_chats(self, user_id: int) -> List[Chat]:
        query = select(Chat).join(ChatMember).where(ChatMember.user_id == user_id)
        return await self._execute_query(query)

    async def create(self, chat: Chat) -> Chat:
        chat = await self._add(chat)
        await self._commit()
        return chat

    async def delete(self, chat_id: int) -> Chat:
        chat = await self._get_by_id(Chat, chat_id)
        return await self._delete(chat)



class ChatMemberRepository(BaseRepository):
    async def create(self, chat_member: ChatMember) -> ChatMember:
        chat_member =  await self._add(chat_member)
        await self._commit()
        return chat_member

    async def add_member(self, member: ChatMember) -> ChatMember:
        return await self._add(member)

    async def get_chat_members(self, chat_id: int) -> List[ChatMember]:
        query = select(ChatMember).where(ChatMember.chat_id == chat_id)
        return await self._execute_query(query)

    async def get_member(self, chat_id: int, user_id: int) -> Optional[ChatMember]:
        result = await self.session.execute(
            select(ChatMember).filter_by(chat_id=chat_id, user_id=user_id)
        )
        return result.scalars().first()

    async def remove_member(self, chat_id: int, user_id: int) -> ChatMember:
        member = await self._get_by_composite_key(ChatMember, chat_id=chat_id, user_id=user_id)
        return await self._delete(member)


class MessageRepository(BaseRepository):
    async def create(self, message: Message) -> Message:
        return await self._add(message)

    async def get_by_id(self, message_id: int) -> Message:
        return await self._get_by_id(Message,message_id)

    async def get_chat_messages(self, chat_id: int) -> List[Message]:
        query = select(Message).where(Message.chat_id == chat_id)
        return await self._execute_query(query)

    async def delete(self, message_id: int) -> Message:
        message = await self._get_by_id(Message,message_id)
        return await self._delete(message)

    async def update(self, message: Message) -> Message:
        await self.session.commit()
        return message

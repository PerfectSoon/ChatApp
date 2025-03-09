from dataclasses import dataclass
from typing import List, Optional

from database.repositories import MessageRepository
from database.schemas import ChatCreate
from database.models import ChatMember, Chat, Message


@dataclass(kw_only=True, frozen=True, slots=True)
class MessageService:
    messagerepo: MessageRepository

    async def create(self, chat_id: int, sender_id: int, text: str) -> Optional[Message]:
        message = Message(
            chat_id=chat_id,
            sender_id=sender_id,
            text=text,
        )
        return await self.messagerepo.create(message)

    async def get_chat_messages(self, chat_id: int) -> List[Message]:
        return await self.messagerepo.get_chat_messages(chat_id)

    async def mark_as_read(self, message_id: int) -> Optional[Message]:
        message = await self.messagerepo.get_by_id(message_id)
        if not message:
            return None
        message.is_read = True
        return await self.messagerepo.update(message)

    async def delete_message(self, message_id: int) -> Optional[Message]:
        return await self.messagerepo.delete(message_id)
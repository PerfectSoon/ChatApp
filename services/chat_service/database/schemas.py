from datetime import datetime

from enum import Enum
from pydantic import BaseModel, Field


class ChatType(str, Enum):
    private = "private"
    public = "public"

class ChatCreate(BaseModel):
    type: ChatType = Field(default=ChatType.private)
    name: str

class ChatOut(BaseModel):
    id: int
    name: str
    type: str
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True


class UserToChat(BaseModel):
    chat_id: int
    user_id: int

class ChatMemberOut(BaseModel):
    chat_id: int
    user_id: int
    joined_at: datetime
    role: str

    class Config:
        from_attributes = True

class MessageOut(BaseModel):
    id:int
    chat_id: int
    sender_id: int
    text: str
    sent_at: datetime
    is_read: bool

    class Config:
        from_attributes = True



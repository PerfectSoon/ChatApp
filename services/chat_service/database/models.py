from sqlalchemy import String, Integer, ForeignKey, DateTime, Index, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(50), Enum("public", "private"), default="private")
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    owner_id: Mapped[int] = mapped_column(Integer)

    members = relationship("ChatMember", back_populates="chat", cascade="all, delete")

    messages = relationship("Message", back_populates="chat", cascade="all, delete")


class ChatMember(Base):
    __tablename__ = "chat_members"

    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey("chats.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer,  primary_key=True)

    joined_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    role: Mapped[str] = mapped_column(String, Enum("member", "admin"), default="member",nullable=False)

    chat = relationship("Chat", back_populates="members")

    __table_args__ = (
        Index('idx_user_id', user_id),
    )

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey("chats.id"))
    sender_id: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(String(500))
    sent_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    chat = relationship("Chat", back_populates="messages")
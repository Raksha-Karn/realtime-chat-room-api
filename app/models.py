from sqlalchemy import func, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    messages: Mapped[list["Message"]] = relationship(back_populates="sender")
    created_rooms: Mapped[list["Room"]] = relationship(back_populates="creator")
    is_deleted: Mapped[bool] = mapped_column(default=False)


class Room(Base):
    __tablename__ = "rooms"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    messages: Mapped[list["Message"]] = relationship(back_populates="room")
    creator: Mapped["User"] = relationship(back_populates="created_rooms")


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(2000), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True, nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    room: Mapped["Room"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship(back_populates="messages")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RoomMember(Base):
    __tablename__ = "room_members"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), primary_key=True, index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user: Mapped["User"] = relationship()
    room: Mapped["Room"] = relationship()
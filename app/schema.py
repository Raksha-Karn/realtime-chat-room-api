from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip()


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    model_config = {"from_attributes": True}


class UserSearchOut(BaseModel):
    id: int
    username: str
    model_config = {"from_attributes": True}


class RoomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class RoomOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class MessageOut(BaseModel):
    id: int
    content: str
    message_type: str = "text"
    media_url: Optional[str] = None
    media_name: Optional[str] = None
    sender_id: int
    room_id: int
    username: str
    created_at: datetime
    model_config = {"from_attributes": True}

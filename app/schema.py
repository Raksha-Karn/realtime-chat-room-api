from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    model_config = {"from_attributes": True}


class RoomCreate(BaseModel):
    name: str
    desc: Optional[str] = None


class RoomOut(BaseModel):
    id: int
    name: str
    desc: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class MessageOut(BaseModel):
    id: int
    content: str
    sender_id: int
    room_id: int
    created_at: datetime
    model_config = {"from_attributes": True}
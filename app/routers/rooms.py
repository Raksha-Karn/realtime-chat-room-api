from app.auth import decode_token
from app.database import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.models import Room, Message
from fastapi import APIRouter, Depends, HTTPException, status
from app.schema import RoomOut, RoomCreate, MessageOut

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("", response_model=RoomOut, status_code=201)
def create_room(data: RoomCreate, db: Session = Depends(get_db), user = Depends(decode_token)):
    if db.execute(select(Room).where(Room.name == data.name)).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room name already exists!")
    new_room = Room(
        **data.model_dump(),
        created_by=user.id
    )
    db.add(new_room); db.commit(); db.refresh(new_room)
    return new_room

@router.get("", response_model=list[RoomOut])
def list_rooms(db: Session = Depends(get_db), user = Depends(decode_token)):
    return db.execute(select(Room)).scalars().all()

@router.get("/{room_id}/history", response_model=list[MessageOut])
def room_history(room_id: int, limit: int = 50, db: Session = Depends(get_db), user = Depends(decode_token)):
    messages = (db.execute(select(Message).options(joinedload(Message.sender)).where(Message.room_id == room_id).order_by(Message.created_at.desc()).limit(limit)).scalars().all())
    return [
        {
            "id": msg.id,
            "content": msg.content,
            "sender_id": msg.sender_id,
            "username": msg.sender.username,
            "created_at": msg.created_at,
        }
        for msg in messages
    ]
from app.pubsub import publish_message
from datetime import datetime, UTC
from app.connection_manager import manager
from app.auth import get_user_from_token
from app.database import SessionLocal
from sqlalchemy import select
from app.models import Room, Message
from fastapi import APIRouter, WebSocket, Query, WebSocketDisconnect

router = APIRouter(tags=["chat"])

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, token: str = Query(...)):
    db = SessionLocal()
    try:
        user = get_user_from_token(token, db)
        if not user:
            await websocket.close(code=4001)
            return
        room = db.execute(select(Room).where(Room.id == room_id)).scalar_one_or_none()
        if not room:
            await websocket.close(code=4004)
            return
        await manager.connect(websocket, room_id)
        join_msg = {
            "type": "system",
            "content": f"{user.username} joined the room.",
            "timestamp": datetime.now(UTC).isoformat()
        }
        await publish_message(room_id, join_msg)

        try:
            while True:
                text = await websocket.receive_text()
                print("WEBSOCKET RECEIVED:", text)
                msg = Message(content=text, room_id=room_id, sender_id=user.id)
                db.add(msg); db.commit(); db.refresh(msg)
                print("MESSAGE SAVED:", msg.id)

                payload = {
                    "type": "message",
                    "id": msg.id,
                    "content": text,
                    "username": user.username,
                    "sender_id": user.id,
                    "timestamp": msg.created_at.isoformat()
                }
                print("PUBLISHING MESSAGE:", payload)
                await publish_message(room_id, payload)
        except WebSocketDisconnect:
            manager.disconnect(websocket, room_id)
            leave_msg = {
                "type": "system",
                "content": f"{user.username} left the room.",
                "timestamp": datetime.now(UTC).isoformat()
            }
            await publish_message(room_id, leave_msg)
    finally:
        db.close()
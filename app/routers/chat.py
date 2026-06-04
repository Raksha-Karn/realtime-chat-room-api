from app.pubsub import publish_message
from app.connection_manager import manager
from app.auth import get_user_from_token
from app.database import SessionLocal
from sqlalchemy import select
from app.models import Room, Message
from fastapi import APIRouter, WebSocket, Query, WebSocketDisconnect
import json

router = APIRouter(tags=["chat"])

MAX_TEXT_LENGTH = 2000
MAX_MEDIA_DATA_URL_LENGTH = 2_750_000
ALLOWED_MEDIA_PREFIXES = {
    "image": ("data:image/png", "data:image/jpeg", "data:image/gif", "data:image/webp"),
    "audio": ("data:audio/webm", "data:audio/mpeg", "data:audio/mp4", "data:audio/wav", "data:audio/ogg"),
    "video": ("data:video/mp4", "data:video/webm", "data:video/ogg"),
    "file": ("data:application/pdf", "data:text/plain", "data:application/zip", "data:application/octet-stream"),
}

def is_allowed_media_url(message_type: str, media_url: str | None) -> bool:
    if not media_url:
        return True
    return str(media_url).startswith(ALLOWED_MEDIA_PREFIXES.get(message_type, ()))

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

        try:
            while True:
                text = await websocket.receive_text()
                try:
                    incoming = json.loads(text)
                    if not isinstance(incoming, dict):
                        incoming = {"content": text, "message_type": "text"}
                except json.JSONDecodeError:
                    incoming = {"content": text, "message_type": "text"}

                message_type = incoming.get("message_type") or incoming.get("type") or "text"
                if message_type not in {"text", "image", "file", "audio", "video"}:
                    message_type = "text"

                content = str(incoming.get("content") or "").strip()
                media_url = incoming.get("media_url")
                media_name = incoming.get("media_name")
                if len(content) > MAX_TEXT_LENGTH:
                    await websocket.send_text(json.dumps({"type": "error", "content": "Message is too long."}))
                    continue
                if media_url and len(str(media_url)) > MAX_MEDIA_DATA_URL_LENGTH:
                    await websocket.send_text(json.dumps({"type": "error", "content": "Media file is too large."}))
                    continue
                if media_url and not is_allowed_media_url(message_type, media_url):
                    await websocket.send_text(json.dumps({"type": "error", "content": "Unsupported media type."}))
                    continue
                if media_name and len(str(media_name)) > 255:
                    media_name = str(media_name)[:255]
                if not content and not media_url:
                    continue

                msg = Message(
                    content=content,
                    message_type=message_type,
                    media_url=media_url,
                    media_name=media_name,
                    room_id=room_id,
                    sender_id=user.id,
                )
                db.add(msg); db.commit(); db.refresh(msg)

                payload = {
                    "type": "message",
                    "id": msg.id,
                    "content": content,
                    "message_type": msg.message_type,
                    "media_url": msg.media_url,
                    "media_name": msg.media_name,
                    "username": user.username,
                    "sender_id": user.id,
                    "room_id": room_id,
                    "timestamp": msg.created_at.isoformat()
                }
                await publish_message(room_id, payload)
        except WebSocketDisconnect:
            manager.disconnect(websocket, room_id)
    finally:
        db.close()

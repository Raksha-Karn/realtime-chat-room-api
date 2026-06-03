from collections import defaultdict
from fastapi import WebSocket
import json


class ConnectionManager:
    def __init__(self):
        self.rooms: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, room_id: int):
        await websocket.accept()
        self.rooms[room_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, room_id: int):
        if websocket not in self.rooms.get(room_id, []):
            return
        self.rooms[room_id].remove(websocket)
        if not self.rooms[room_id]:
            del self.rooms[room_id]
    
    async def broadcast_to_room(self, room_id: int, message: dict):
        payload = json.dumps(message)
        dead = []

        for ws in list(self.rooms.get(room_id, [])):
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, room_id)

manager = ConnectionManager()

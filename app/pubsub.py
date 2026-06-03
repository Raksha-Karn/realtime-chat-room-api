import json
import os
import uuid

import redis.asyncio as aioredis
from dotenv import load_dotenv

from .connection_manager import manager

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
INSTANCE_ID = str(uuid.uuid4())

redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

async def publish_message(room_id: int, message: dict):
    await manager.broadcast_to_room(room_id, message)

    channel = f"room:{room_id}"
    event = {
        "origin": INSTANCE_ID,
        "message": message,
    }
    try:
        await redis_client.publish(channel, json.dumps(event))
    except Exception as e:
        print(f"Redis publish error: {e}")

async def redis_listener():
    pubsub = redis_client.pubsub()
    try:
        await pubsub.psubscribe("room:*")
        print("REDIS LISTENER STARTED")

        async for message in pubsub.listen():
            print("REDIS RECEIVED:", message)
            if message["type"] != "pmessage":
                continue
            try:
                channel = message["channel"]
                room_id = int(channel.split(":")[1])
                data = json.loads(message["data"])

                if data.get("origin") == INSTANCE_ID:
                    continue

                payload = data.get("message", data)
                print("BROADCASTING:", room_id, payload)
                await manager.broadcast_to_room(room_id, payload)
            except Exception as e:
                print(f"Pub/sub error: {e}")
    except Exception as e:
        print(f"Redis listener error: {e}")
    finally:
        await pubsub.close()

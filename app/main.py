from app.routers import users, rooms, chat
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
from app.pubsub import redis_listener
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    listener_task = asyncio.create_task(redis_listener())
    yield
    listener_task.cancel()

app = FastAPI(title="Chat API", version="1.0.0", lifespan=lifespan)
app.include_router(users.router)
app.include_router(rooms.router)
app.include_router(chat.router)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def frontend():
    return FileResponse(static_dir / "index.html")

@app.get("/health")
def health():
    return {"status": "ok"}
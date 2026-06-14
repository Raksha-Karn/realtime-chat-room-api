import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.main import app
from app.database import Base, get_db

TEST_DB = "sqlite:///./test.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=engine)

@pytest.fixture(autouse=True)
def client():
    Base.metadata.create_all(bind=engine)
    def override():
        yield TestSession()
    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

def register_and_login(client, email="a@b.com", username="alice"):
    client.post("/auth/register", json={"email": email, "username": username, "password": "pw12345678"})
    r = client.post("/auth/login", data={"username": email, "password": "pw12345678"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_room(client):
    headers = register_and_login(client)
    r = client.post("/rooms", json={"name": "general"}, headers=headers)
    assert r.status_code == 201
    assert r.json()['name'] == 'general'

def test_duplicate_room_name(client):
    headers = register_and_login(client)
    client.post("/rooms", json={"name": "general"}, headers=headers)
    r = client.post("/rooms", json={"name": "general"}, headers=headers)
    assert r.status_code == 400

def test_list_rooms(client):
    headers = register_and_login(client)
    client.post("/rooms", json={"name": "general"}, headers=headers)
    r = client.get("/rooms", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1

def test_room_history_empty(client):
    headers = register_and_login(client)
    r_room = client.post("/rooms", json={"name": "general"}, headers=headers)
    r_room_id = r_room.json()["id"]
    r = client.get(f"/rooms/{r_room_id}/history", headers=headers)
    assert r.status_code == 200
    assert r.json() == []

def test_unauthenticated_room_access(client):
    r = client.get("/rooms")
    assert r.status_code == 401
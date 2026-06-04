# Real-Time Chat App

<p align="center">
  <strong>A real-time room chat application with authentication, message history, media sharing, voice notes, global search, and emoji support.</strong>
</p>

<p align="center">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
  <img alt="Redis" src="https://img.shields.io/badge/Redis-FF4438?style=for-the-badge&logo=redis&logoColor=white">
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</p>

<p align="center">
  <a href="#features">Features</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#system-design">System Design</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#api-surface">API Surface</a>
</p>

---

## Features

- JWT-based register, login, and authenticated session handling.
- Realtime room messaging over WebSockets.
- Persistent message history loaded when users enter a room.
- Text, image, audio, video, file, and voice-note messages.
- Emoji picker in the composer.
- Global search for users and message content.
- Room creation and room list navigation.
- Redis pub/sub support for multi-worker message broadcast.
- PostgreSQL persistence with SQLAlchemy models and Alembic migrations.
- Static frontend served directly by FastAPI.

## UI Preview

### Register/Login
JWT Based Authentication!

---
![Login](./screenshots/signupo.png)

### Home Page
Select a room to get started!

---
![Home](./screenshots/homee.png)

### New Room
Create your own messaging room!

---
![Room](./screenshots/room.png)

### Group Chat
Connect to people and share your thoughts!

---
![GC](./screenshots/gc.png)




## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | FastAPI, Python 3.12 |
| Realtime | WebSockets, Redis pub/sub |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Auth | JWT, OAuth2 password flow, passlib/bcrypt |
| Frontend | HTML, Tailwind CDN, vanilla JavaScript |
| Runtime | Uvicorn |
| Local infra | Docker, Docker Compose |


## Architecture

```mermaid
flowchart LR
    Browser["Browser UI<br/>HTML + Tailwind + JS"]:::client
    FastAPI["FastAPI App<br/>REST + WebSocket"]:::api
    Auth["Auth Layer<br/>JWT validation"]:::auth
    Rooms["Rooms API<br/>history + search"]:::api
    WS["Connection Manager<br/>room sockets"]:::realtime
    Redis["Redis Pub/Sub<br/>cross-instance fanout"]:::redis
    DB[("PostgreSQL<br/>users rooms messages")]:::db

    Browser -->|"REST: auth, rooms, search"| FastAPI
    Browser <-->|"WebSocket: /ws/{room_id}"| FastAPI
    FastAPI --> Auth
    FastAPI --> Rooms
    FastAPI --> WS
    Auth --> DB
    Rooms --> DB
    FastAPI -->|"publish room events"| Redis
    Redis -->|"fanout events"| WS
    WS -->|"broadcast message"| Browser
    FastAPI -->|"persist messages"| DB

    classDef client fill:#E0F2FE,stroke:#0284C7,color:#075985
    classDef api fill:#DCFCE7,stroke:#16A34A,color:#14532D
    classDef auth fill:#FEF3C7,stroke:#D97706,color:#78350F
    classDef realtime fill:#FCE7F3,stroke:#DB2777,color:#831843
    classDef redis fill:#FEE2E2,stroke:#DC2626,color:#7F1D1D
    classDef db fill:#EDE9FE,stroke:#7C3AED,color:#3B0764
```

## System Design

### Message Delivery Flow

```mermaid
sequenceDiagram
    participant U as User Browser
    participant A as FastAPI WebSocket
    participant D as PostgreSQL
    participant R as Redis Pub/Sub
    participant P as Peers in Room

    U->>A: Connect /ws/{room_id}?token=JWT
    A->>A: Validate token and room
    U->>A: Send structured message JSON
    A->>A: Validate type, size, and media prefix
    A->>D: Persist message
    D-->>A: Message id + timestamp
    A->>R: Publish room event
    A-->>U: Broadcast message
    R-->>P: Fan out to other app instances
```

### Data Model

```mermaid
erDiagram
    USERS ||--o{ ROOMS : creates
    USERS ||--o{ MESSAGES : sends
    ROOMS ||--o{ MESSAGES : contains
    USERS ||--o{ ROOM_MEMBERS : joins
    ROOMS ||--o{ ROOM_MEMBERS : has

    USERS {
        int id PK
        string email UK
        string username UK
        string hashed_password
        bool is_active
        bool is_deleted
        datetime created_at
    }

    ROOMS {
        int id PK
        string name
        string description
        int created_by FK
        datetime created_at
    }

    MESSAGES {
        int id PK
        string content
        string message_type
        text media_url
        string media_name
        int room_id FK
        int sender_id FK
        datetime created_at
    }

    ROOM_MEMBERS {
        int user_id FK
        int room_id FK
        datetime joined_at
    }
```

## API Surface

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Create a user |
| `POST` | `/auth/login` | Get a JWT access token |
| `GET` | `/auth/me` | Get current user profile |
| `GET` | `/auth/users/search?q=` | Search users by username |
| `POST` | `/rooms` | Create a room |
| `GET` | `/rooms` | List rooms |
| `GET` | `/rooms/{room_id}/history` | Load room message history |
| `GET` | `/rooms/search/messages?q=` | Search messages |
| `WS` | `/ws/{room_id}?token=` | Realtime room messaging |

## Quick Start

Create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:password@db/chatapi
REDIS_URL=redis://redis:6379/0
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
PORT=8000
```

Run with Docker Compose:

```bash
docker compose up --build
```

Apply migrations:

```bash
docker compose exec api alembic upgrade head
```

Open the app:

```text
http://localhost:8000
```

## Local Development

Install dependencies with `uv`:

```bash
uv sync
```

Run migrations:

```bash
uv run alembic upgrade head
```

Start the API:

```bash
uv run uvicorn app.main:app --reload
```


## Realtime Message Shape

```json
{
  "message_type": "text",
  "content": "Hello team"
}
```

Media messages include a browser data URL:

```json
{
  "message_type": "image",
  "content": "Screenshot from today",
  "media_url": "data:image/png;base64,...",
  "media_name": "screenshot.png"
}
```

Supported `message_type` values:

- `text`
- `image`
- `audio`
- `video`
- `file`

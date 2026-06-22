from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import os
import redis.asyncio as aioredis
from uuid import UUID
from app.constants import LOCAL_FRONTEND_URL, REDIS_URL
from app.routers import auth, users, projects, topics, experiments, ingest, assignments, events, flags, alerts

# Background task that starts when the app starts & subscribe to Redis channels
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(redis_listener())
    yield
    
# Initialize the main web app object -- this orchestrates the entire API
app = FastAPI(lifespan=lifespan)

# Read frontend URL from Railway's environment
frontend_url = os.getenv("FRONTEND_URL", LOCAL_FRONTEND_URL)

# Configuring CORS -- set to accept all requests for development
origins = [
    frontend_url,
    LOCAL_FRONTEND_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(topics.router)
app.include_router(experiments.router)
app.include_router(ingest.router)
app.include_router(assignments.router)
app.include_router(events.router)
app.include_router(flags.router)
app.include_router(alerts.router)

# test endpoint -- just to see if things work
@app.get("/")
def test():
    return {"message": "hello"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/trigger-ingestion")
def trigger_ingestion():
    from app.workers.tasks import schedule_ingestion
    schedule_ingestion.delay()
    return {"status": "ingestion triggered"}

'''
WebSocket stuff below
'''

# WebSocket connection manager class
class ConnectionManager:
    def __init__(self):
        self.connections = dict()

    # Adds a new WebSocket connection to the list
    def connect(self, websocket: WebSocket, project_id: UUID):
        if project_id not in self.connections:
            self.connections[project_id] = [websocket]
        else:
            self.connections[project_id].append(websocket)
    
    # Removes a WebSocket connection from the list
    def disconnect(self, websocket: WebSocket, project_id: UUID):
        if project_id in self.connections:
            try:
                self.connections[project_id].remove(websocket)
            except ValueError:
                pass

            if not self.connections[project_id]:
                del self.connections[project_id]
    
    # Sends a message to all connections watching a specific project
    async def broadcast(self, project_id: UUID, message):
        websockets = self.connections.get(project_id, [])
        for ws in websockets:
            try:
                await ws.send_text(message)
            except Exception:
                continue

# Instantiate the WebSocket connection manager
manager = ConnectionManager()

# WebSocket endpoint
@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: UUID):
    await websocket.accept()
    manager.connect(websocket, project_id)
    try: 
        while True:
            data = await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket, project_id)

# Redis listener
async def redis_listener():
    while True:    
        try:
            redis_url = os.getenv("REDIS_URL") or REDIS_URL
            # connect to Redis
            r = aioredis.Redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=30,
                socket_connect_timeout=30,
                socket_keepalive=True,
            )
            
            # subscribe to a pattern
            async with r.pubsub() as pubsub:
                await pubsub.psubscribe("alerts:*")
                # loop waiting for messages
                async for message in pubsub.listen():
                    if message["type"] != "pmessage":
                        continue
                    try:
                        data = json.loads(message["data"])
                    except Exception:
                        continue
                    channel = message["channel"]
                    project_id = channel.split(":")[1]
                    try:
                        project_uuid = UUID(project_id)
                    except Exception:
                        continue
                    await manager.broadcast(project_uuid, json.dumps(data))
        except Exception as e:
            print("Redis listener error:", e)
            await asyncio.sleep(5)
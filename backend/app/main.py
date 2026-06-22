from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import os
import redis.asyncio as aioredis
from uuid import UUID
from app.constants import REDIS_HOST, REDIS_PORT, LOCAL_FRONTEND_URL
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

# test endpoint -- just to see if things work
@app.get("/")
def test():
    return {"message": "hello"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

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
            self.connections[project_id].remove(websocket)
    
    # Sends a message to all connections watching a specific project
    async def broadcast(self, project_id: UUID, message):
        websockets = self.connections[project_id]
        for ws in websockets:
            await ws.send_text(message)

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
    except:
        manager.disconnect(websocket, project_id)

# Redis listener
async def redis_listener():
    try:
        # connect to Redis
        r = aioredis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=0,
            password=None,
            encoding="utf-8",
            decode_responses=True
        )
        # subscribe to a pattern
        async with r.pubsub() as pubsub:
            await pubsub.psubscribe("alerts:*")
            # loop waiting for messages
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    data = json.loads(message["data"])
                    channel = message["channel"]
                    project_id = channel.split(":")[1]
                    await manager.broadcast(UUID(project_id), json.dumps(data))
    except Exception as e:
        print(e)
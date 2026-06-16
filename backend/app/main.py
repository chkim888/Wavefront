from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, projects, topics, experiments, ingest, assignments, events, flags

# Initialize the main web app object -- this orchestrates the entire API
app = FastAPI()

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

# Configuring CORS -- set to accept all requests for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# test endpoint -- just to see if things work
@app.get("/")
def test():
    return {"message": "hello"}
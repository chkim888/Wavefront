from fastapi import FastAPI
from app.routers import auth, users, projects, topics, experiments

# Initialize the main web app object -- this orchestrates the entire API
app = FastAPI()

### routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(topics.router)
app.include_router(experiments.router)

# test endpoint -- just to see if things work
@app.get("/")
def test():
    return {"message": "hello"}
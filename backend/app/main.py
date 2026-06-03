from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.projects import router as projects_router
from app.routers.topics import router as topics_router
from app.routers.experiments import router as experiments_router

# Initialize the main web app object -- this orchestrates the entire API
app = FastAPI()

### routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(topics_router)
app.include_router(experiments_router)

# test endpoint -- just to see if things work
@app.get("/")
def test():
    return {"message": "hello"}
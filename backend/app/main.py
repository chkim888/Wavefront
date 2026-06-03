from fastapi import FastAPI
from app.routers.auth import router as auth_router

# Initialize the main web app object -- this orchestrates the entire API
app = FastAPI()

### routers
app.include_router(auth_router)

# test endpoint -- just to see if things work
@app.get("/")
def test():
    return {"message": "hello"}
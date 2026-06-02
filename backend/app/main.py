from fastapi import FastAPI

# Initialize the main web app object -- this orchestrates the entire API
app = FastAPI()

# test endpoint -- just to see if things work
@app.get("/")
def test():
    return {"message": "hello"}
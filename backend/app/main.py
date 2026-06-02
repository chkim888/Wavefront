from fastapi import FastAPI

app = FastAPI()

# test endpoint -- just to see if things work
@app.get("/")
def test():
    return {"message": "hello"}
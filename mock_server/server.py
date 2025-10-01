from fastapi import FastAPI

app = FastAPI(title="ReqTools Mock API")


@app.get("/")
def root():
    return {
        "message": "Hello World",
        "status": "ok",
        "data": {"id": 1, "name": "Sample Item", "value": 42},
    }

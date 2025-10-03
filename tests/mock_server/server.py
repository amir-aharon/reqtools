from fastapi import FastAPI, Request

app = FastAPI(title="ReqTools Mock API")


@app.post("/echo")
async def echo(request: Request):
    data = await request.json()
    return {"echo": data}


@app.get("/")
def root():
    return {
        "message": "Hello World",
        "status": "ok",
        "data": {"id": 1, "name": "Sample Item", "value": 42},
    }

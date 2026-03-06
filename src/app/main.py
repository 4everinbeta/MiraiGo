from fastapi import FastAPI
from src.app.api.v1 import search

app = FastAPI(title="MiraiGo API")

app.include_router(search.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.api.v1 import search

app = FastAPI(title="MiraiGo API")

# Configure CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}

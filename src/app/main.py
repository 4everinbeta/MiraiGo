from fastapi import FastAPI

app = FastAPI(title="MiraiGo API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

from fastapi import FastAPI

from app.routers import images

app = FastAPI(title="OCTera API")
app.include_router(images.router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

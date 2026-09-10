from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import images

app = FastAPI(title="OCTera API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(images.router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

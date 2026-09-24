"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes.chat import router as chat_router
from ml.rag.ingest import ingest_profile_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Fill an empty profile store once when the process starts."""
    ingest_profile_if_empty()
    yield


app = FastAPI(title="qa-for-me", lifespan=lifespan)
app.include_router(chat_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the API process is up."""
    return {"status": "ok"}

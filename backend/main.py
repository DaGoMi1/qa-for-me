"""FastAPI application entrypoint."""

from fastapi import FastAPI

from backend.api.routes.chat import router as chat_router

app = FastAPI(title="qa-for-me")
app.include_router(chat_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the API process is up."""
    return {"status": "ok"}

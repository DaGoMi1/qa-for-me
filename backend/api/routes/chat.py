"""Chat route. Graph invocation is left for a later step."""

from fastapi import APIRouter, HTTPException

from backend.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Accept a question. The retrieve-then-generate graph is not wired yet."""
    raise HTTPException(status_code=501, detail="Chat graph is not implemented yet.")

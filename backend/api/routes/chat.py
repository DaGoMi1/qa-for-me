"""Chat route that runs the retrieve-then-generate graph."""

from typing import Any

from fastapi import APIRouter, Depends

from backend.schemas.chat import ChatRequest, ChatResponse
from ml.graph.builder import build_graph

router = APIRouter()


def get_chat_graph() -> Any:
    """Compile the default graph from settings and data/chroma."""
    return build_graph()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    graph: Any = Depends(get_chat_graph),
) -> ChatResponse:
    """Accept a question and return the graph answer."""
    result = graph.invoke(
        {
            "question": request.question,
            "history": [message.model_dump() for message in request.history],
            "context": [],
            "answer": "",
        }
    )
    return ChatResponse(answer=result["answer"])

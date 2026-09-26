"""Chat route that runs the retrieve-then-generate graph."""

import logging
import time
from typing import Any

from fastapi import APIRouter, Depends

from backend.schemas.chat import ChatRequest, ChatResponse
from ml.graph.builder import build_graph

router = APIRouter()
logger = logging.getLogger("uvicorn.error")


def get_chat_graph() -> Any:
    """Compile the default graph from settings and data/chroma."""
    return build_graph()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    graph: Any = Depends(get_chat_graph),
) -> ChatResponse:
    """Accept a question and return the graph answer."""
    started = time.perf_counter()
    result = graph.invoke(
        {
            "question": request.question,
            "history": [message.model_dump() for message in request.history],
            "intent": "",
            "search_query": "",
            "context": [],
            "answer": "",
        }
    )
    latency_ms = round((time.perf_counter() - started) * 1000)
    intent = str(result.get("intent") or "")
    search_query = str(result.get("search_query") or "")
    answer = str(result.get("answer") or "")
    context = result.get("context") or []
    source = "projects.md" if intent == "projects" else "bio.md"
    logger.info(
        "chat\n"
        f"intent={intent}\n"
        f"search_query={search_query}\n"
        f"source={source}\n"
        f"n_context={len(context)}\n"
        f"n_history={len(request.history)}\n"
        f"latency_ms={latency_ms}\n"
        f"question_chars={len(request.question)}\n"
        f"answer_chars={len(answer)}"
    )
    return ChatResponse(answer=answer)

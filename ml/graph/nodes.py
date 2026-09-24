"""Graph nodes for retrieval and answer generation."""

from typing import Protocol

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI

from backend.core.config import get_settings
from ml.graph.state import GraphState, HistoryMessage
from ml.rag.vectorstore import get_vector_store

_HISTORY_TURNS = 4


class _ChatMessage(Protocol):
    """Model reply. Only the text is used."""

    content: str


class _ChatModel(Protocol):
    """Anything that turns a prompt string into a message with content."""

    def invoke(self, prompt: str) -> _ChatMessage: ...


def _recent_history(history: list[HistoryMessage]) -> list[HistoryMessage]:
    """Keep only the last few turns so prompts stay short."""
    return history[-_HISTORY_TURNS:]


def _format_history(history: list[HistoryMessage]) -> str:
    """Render history lines for search and prompts."""
    lines: list[str] = []
    for message in _recent_history(history):
        lines.append(f"{message['role']}: {message['content']}")
    return "\n".join(lines)


def _search_query(state: GraphState) -> str:
    """Combine recent history with the current question for retrieval."""
    history_text = _format_history(state.get("history", []))
    if not history_text:
        return state["question"]
    return f"{history_text}\nuser: {state['question']}"


def retrieve(state: GraphState, vector_store: Chroma | None = None) -> GraphState:
    """Load profile chunks relevant to the question and recent history."""
    store = vector_store or get_vector_store()
    documents = store.similarity_search(_search_query(state), k=4)
    return {
        "question": state["question"],
        "history": state.get("history", []),
        "context": [document.page_content for document in documents],
        "answer": "",
    }


def generate(state: GraphState, model: _ChatModel | None = None) -> GraphState:
    """Draft an answer from the retrieved context and recent history."""
    chat = model or _default_chat_model()
    context = "\n".join(state["context"])
    history_text = _format_history(state.get("history", []))
    history_block = (
        f"이전 대화:\n{history_text}\n\n" if history_text else ""
    )
    prompt = (
        "다음 프로필 내용만 보고 질문에 한국어로 답하세요. "
        "이전 대화가 있으면 이어 묻기를 반영하되, 프로필 내용에 없는 것은 모른다고 답하세요.\n\n"
        f"내용:\n{context}\n\n"
        f"{history_block}"
        f"질문: {state['question']}"
    )
    response = chat.invoke(prompt)
    return {
        "question": state["question"],
        "history": state.get("history", []),
        "context": state["context"],
        "answer": response.content,
    }


def _default_chat_model() -> ChatOpenAI:
    """Open the configured chat model. Tests pass their own model instead."""
    settings = get_settings()
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
    )

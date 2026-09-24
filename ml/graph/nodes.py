"""Graph nodes for rewrite, retrieval, and answer generation."""

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
    """Render history lines for prompts."""
    lines: list[str] = []
    for message in _recent_history(history):
        lines.append(f"{message['role']}: {message['content']}")
    return "\n".join(lines)


def _pass_through(state: GraphState, **updates: object) -> GraphState:
    """Keep shared fields and apply local updates."""
    return {
        "question": state["question"],
        "history": state.get("history", []),
        "search_query": state.get("search_query", ""),
        "context": state.get("context", []),
        "answer": state.get("answer", ""),
        **updates,  # type: ignore[misc]
    }


def rewrite(state: GraphState, model: _ChatModel | None = None) -> GraphState:
    """Build a standalone search query from the question and history."""
    history = state.get("history", [])
    if not history:
        return _pass_through(state, search_query=state["question"], context=[], answer="")

    chat = model or _default_chat_model()
    history_text = _format_history(history)
    prompt = (
        "이전 대화와 이어 묻기를 보고, 프로필 문서 검색에 쓸 한국어 질문 한 문장만 쓰세요. "
        "설명이나 따옴표 없이 검색어만 출력하세요.\n\n"
        f"이전 대화:\n{history_text}\n\n"
        f"이어 묻기: {state['question']}"
    )
    response = chat.invoke(prompt)
    search_query = response.content.strip() or state["question"]
    return _pass_through(state, search_query=search_query, context=[], answer="")


def retrieve(state: GraphState, vector_store: Chroma | None = None) -> GraphState:
    """Load profile chunks for the rewritten search query."""
    store = vector_store or get_vector_store()
    query = state.get("search_query") or state["question"]
    documents = store.similarity_search(query, k=4)
    return _pass_through(
        state,
        context=[document.page_content for document in documents],
        answer="",
    )


def generate(state: GraphState, model: _ChatModel | None = None) -> GraphState:
    """Draft an answer from the retrieved context and recent history."""
    chat = model or _default_chat_model()
    context = "\n".join(state["context"])
    history_text = _format_history(state.get("history", []))
    history_block = (
        f"이전 대화:\n{history_text}\n\n" if history_text else ""
    )
    prompt = (
        "당신은 이다검입니다. 아래 사실만 근거로 질문에 한국어로 답하세요. "
        "나/저는으로 직접 말하세요. "
        "프로필, 문서, 검색 결과 같은 말은 쓰지 마세요. "
        "이전 대화가 있으면 이어 묻기를 반영하세요. "
        "사실에 없으면 짧게 모른다고만 하세요.\n\n"
        f"내가 알아도 되는 사실:\n{context}\n\n"
        f"{history_block}"
        f"질문: {state['question']}"
    )
    response = chat.invoke(prompt)
    return _pass_through(state, answer=response.content)


def _default_chat_model() -> ChatOpenAI:
    """Open the configured chat model. Tests pass their own model instead."""
    settings = get_settings()
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
    )

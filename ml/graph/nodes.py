"""Graph nodes for retrieval and answer generation."""

from typing import Protocol

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI

from backend.core.config import get_settings
from ml.graph.state import GraphState
from ml.rag.vectorstore import get_vector_store


class _ChatMessage(Protocol):
    """Model reply. Only the text is used."""

    content: str


class _ChatModel(Protocol):
    """Anything that turns a prompt string into a message with content."""

    def invoke(self, prompt: str) -> _ChatMessage: ...


def retrieve(state: GraphState, vector_store: Chroma | None = None) -> GraphState:
    """Load profile chunks relevant to the question."""
    store = vector_store or get_vector_store()
    documents = store.similarity_search(state["question"], k=4)
    return {
        "question": state["question"],
        "context": [document.page_content for document in documents],
        "answer": "",
    }


def generate(state: GraphState, model: _ChatModel | None = None) -> GraphState:
    """Draft an answer from the retrieved context."""
    chat = model or _default_chat_model()
    context = "\n".join(state["context"])
    prompt = (
        "다음 프로필 내용만 보고 질문에 한국어로 답하세요. "
        "내용에 없으면 모른다고 답하세요.\n\n"
        f"내용:\n{context}\n\n"
        f"질문: {state['question']}"
    )
    response = chat.invoke(prompt)
    return {
        "question": state["question"],
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

"""POST /chat uses an injected graph so tests skip OpenAI."""

from fastapi.testclient import TestClient
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from backend.api.routes.chat import get_chat_graph
from backend.main import app
from ml.graph.builder import build_graph
from ml.rag.loader import PROFILE_DIR
from ml.rag.vectorstore import get_vector_store


class _FixedEmbedding(Embeddings):
    """Return the same vector for every text. No API call."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0]


class _Message:
    """Fixed model reply. No API call."""

    def __init__(self, content: str) -> None:
        self.content = content


class _RoutingModel:
    """Prepare-shaped reply for prepare prompts; fixed answer otherwise."""

    def invoke(self, prompt: str) -> _Message:
        if "intent: bio 또는 projects" in prompt:
            return _Message("intent: bio\nsearch_query: 어디서 살아?")
        return _Message("부산에서 살고 있습니다.")


def test_chat_returns_fake_answer(tmp_path) -> None:
    """POST /chat returns the fake model answer when the graph is overridden."""
    store = get_vector_store(
        embeddings=_FixedEmbedding(),
        persist_directory=str(tmp_path),
    )
    store.add_documents(
        [
            Document(
                page_content="이다검은 부산에서 살고 있습니다.",
                metadata={"source": str(PROFILE_DIR / "bio.md")},
            )
        ]
    )
    graph = build_graph(vector_store=store, model=_RoutingModel())
    app.dependency_overrides[get_chat_graph] = lambda: graph
    client = TestClient(app)

    try:
        response = client.post(
            "/chat",
            json={
                "question": "어디서 살아?",
                "history": [
                    {"role": "user", "content": "안녕"},
                    {"role": "assistant", "content": "안녕하세요."},
                ],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"answer": "부산에서 살고 있습니다."}

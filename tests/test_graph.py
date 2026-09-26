"""Compiled graph runs prepare, retrieve, then generate."""

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

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


def test_graph_retrieves_then_answers(tmp_path) -> None:
    """A bio sentence lands in context and the fake reply becomes the answer."""
    store = get_vector_store(
        embeddings=_FixedEmbedding(),
        persist_directory=str(tmp_path),
    )
    sentence = "이다검은 부산에서 살고 있습니다."
    store.add_documents(
        [
            Document(
                page_content=sentence,
                metadata={"source": str(PROFILE_DIR / "bio.md")},
            )
        ]
    )
    graph = build_graph(vector_store=store, model=_RoutingModel())

    result = graph.invoke(
        {
            "question": "어디서 살아?",
            "history": [],
            "intent": "",
            "search_query": "",
            "context": [],
            "answer": "",
        }
    )

    assert sentence in result["context"]
    assert result["intent"] == "bio"
    assert result["answer"] == "부산에서 살고 있습니다."

"""Compiled graph runs rewrite, retrieve, then generate, without an API call."""

from langchain_core.embeddings import Embeddings

from ml.graph.builder import build_graph
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


class _FixedModel:
    """Return the same sentence for every prompt."""

    def invoke(self, prompt: str) -> _Message:
        return _Message("부산에서 살고 있습니다.")


def test_graph_retrieves_then_answers(tmp_path) -> None:
    """A stored sentence lands in context and the fake reply becomes the answer."""
    store = get_vector_store(
        embeddings=_FixedEmbedding(),
        persist_directory=str(tmp_path),
    )
    sentence = "이다검은 부산에서 살고 있습니다."
    store.add_texts([sentence])
    graph = build_graph(vector_store=store, model=_FixedModel())

    result = graph.invoke(
        {
            "question": "어디서 살아?",
            "history": [],
            "search_query": "",
            "context": [],
            "answer": "",
        }
    )

    assert sentence in result["context"]
    assert result["answer"] == "부산에서 살고 있습니다."

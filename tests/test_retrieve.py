"""Retrieve node reads chunks from a temporary store."""

from langchain_core.embeddings import Embeddings

from ml.graph.nodes import retrieve
from ml.rag.vectorstore import get_vector_store


class _FixedEmbedding(Embeddings):
    """Return the same vector for every text. No API call."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0]


class _SpyStore:
    """Record the search query. Delegates retrieval to a real store."""

    def __init__(self, store) -> None:
        self._store = store
        self.last_query: str | None = None

    def similarity_search(self, query: str, k: int = 4):
        self.last_query = query
        return self._store.similarity_search(query, k=k)


def test_retrieve_puts_sentence_in_context(tmp_path) -> None:
    """A stored sentence is copied into context and the answer stays empty."""
    store = get_vector_store(
        embeddings=_FixedEmbedding(),
        persist_directory=str(tmp_path),
    )
    sentence = "이다검은 부산에서 살고 있습니다."
    store.add_texts([sentence])

    result = retrieve(
        {
            "question": "어디서 살아?",
            "history": [],
            "search_query": "어디서 살아?",
            "context": [],
            "answer": "이전 답",
        },
        vector_store=store,
    )

    assert sentence in result["context"]
    assert result["answer"] == ""


def test_retrieve_uses_search_query_not_history(tmp_path) -> None:
    """similarity_search gets search_query, not raw history text."""
    store = get_vector_store(
        embeddings=_FixedEmbedding(),
        persist_directory=str(tmp_path),
    )
    store.add_texts(["이다검은 부산에서 살고 있습니다."])
    spy = _SpyStore(store)
    rewritten = "이다검이 한 다른 프로젝트 목록"

    retrieve(
        {
            "question": "그거 밖에 없어?",
            "history": [
                {"role": "user", "content": "프로젝트 뭐 있어?"},
                {"role": "assistant", "content": "why-song-serious가 있습니다."},
            ],
            "search_query": rewritten,
            "context": [],
            "answer": "",
        },
        vector_store=spy,
    )

    assert spy.last_query == rewritten
    assert "프로젝트 뭐 있어?" not in (spy.last_query or "")

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


def test_retrieve_puts_sentence_in_context(tmp_path) -> None:
    """A stored sentence is copied into context and the answer stays empty."""
    store = get_vector_store(
        embeddings=_FixedEmbedding(),
        persist_directory=str(tmp_path),
    )
    sentence = "이다검은 부산에서 살고 있습니다."
    store.add_texts([sentence])

    result = retrieve(
        {"question": "어디서 살아?", "context": [], "answer": "이전 답"},
        vector_store=store,
    )

    assert sentence in result["context"]
    assert result["answer"] == ""

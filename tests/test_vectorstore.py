"""Local vector store round trip with a fake embedding."""

from langchain_core.embeddings import Embeddings

from ml.rag.vectorstore import get_vector_store


class _FixedEmbedding(Embeddings):
    """Return the same vector for every text. No API call."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0]


def test_store_finds_inserted_sentence(tmp_path) -> None:
    """A sentence written to a temporary store is returned by search."""
    store = get_vector_store(
        embeddings=_FixedEmbedding(),
        persist_directory=str(tmp_path),
    )
    sentence = "이다검은 부산에서 살고 있습니다."
    store.add_texts([sentence])
    found = store.similarity_search(sentence, k=1)
    assert found[0].page_content == sentence

"""Profile ingestion replaces the collection instead of appending."""

from langchain_core.embeddings import Embeddings

from ml.rag.ingest import ingest_profile
from ml.rag.loader import load_profile_documents
from ml.rag.splitter import split_documents
from ml.rag.vectorstore import get_vector_store


class _FixedEmbedding(Embeddings):
    """Return the same vector for every text. No API call."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0]


def test_second_ingest_does_not_duplicate_chunks(tmp_path) -> None:
    """Running ingestion twice leaves one copy of each chunk."""
    directory = str(tmp_path)
    embeddings = _FixedEmbedding()
    ingest_profile(embeddings=embeddings, persist_directory=directory)
    ingest_profile(embeddings=embeddings, persist_directory=directory)

    stored = get_vector_store(
        embeddings=embeddings,
        persist_directory=directory,
    ).get()["documents"]
    expected = [chunk.page_content for chunk in split_documents(load_profile_documents())]
    assert stored is not None
    assert sorted(stored) == sorted(expected)

"""Load profile markdown, chunk it, and replace the vector store contents."""

from langchain_core.embeddings import Embeddings

from ml.rag.loader import load_profile_documents
from ml.rag.splitter import split_documents
from ml.rag.vectorstore import get_vector_store


def ingest_profile(
    embeddings: Embeddings | None = None,
    persist_directory: str | None = None,
) -> None:
    """Load profile markdown, chunk it, and write embeddings to the vector store."""
    chunks = split_documents(load_profile_documents())
    store = get_vector_store(
        embeddings=embeddings,
        persist_directory=persist_directory,
    )
    store.reset_collection()
    store.add_documents(chunks)

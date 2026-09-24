"""Load profile markdown, chunk it, and replace the vector store contents."""

from langchain_core.embeddings import Embeddings

from ml.rag.loader import load_profile_documents
from ml.rag.splitter import split_documents
from ml.rag.vectorstore import get_vector_store


def profile_store_is_empty(
    embeddings: Embeddings | None = None,
    persist_directory: str | None = None,
) -> bool:
    """Return True when the profile collection has no stored documents."""
    store = get_vector_store(
        embeddings=embeddings,
        persist_directory=persist_directory,
    )
    documents = store.get()["documents"]
    return not documents


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


def ingest_profile_if_empty(
    embeddings: Embeddings | None = None,
    persist_directory: str | None = None,
) -> bool:
    """Ingest only when the store is empty. Return True if ingestion ran."""
    if not profile_store_is_empty(
        embeddings=embeddings,
        persist_directory=persist_directory,
    ):
        return False
    ingest_profile(embeddings=embeddings, persist_directory=persist_directory)
    return True

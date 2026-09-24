"""Open the local Chroma store. Profile documents are not written here."""

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from backend.core.config import get_settings


def get_vector_store(
    embeddings: Embeddings | None = None,
    persist_directory: str | None = None,
) -> Chroma:
    """Open the local vector store at the configured path."""
    settings = get_settings()
    if embeddings is None:
        embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
        )
    return Chroma(
        collection_name="profile",
        embedding_function=embeddings,
        persist_directory=persist_directory or settings.vector_store_path,
    )

"""로컬 Chroma 스토어 열기"""

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from backend.core.config import get_settings


def get_vector_store(
    embeddings: Embeddings | None = None,
    persist_directory: str | None = None,
) -> Chroma:
    """설정된 경로에 있는 로컬 벡터 스토어 열기"""
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

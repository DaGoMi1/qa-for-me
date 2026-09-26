"""프로필 마크다운을 불러와 청크로 나누고, 벡터 스토어에 저장"""

from langchain_core.embeddings import Embeddings

from ml.rag.loader import load_profile_documents
from ml.rag.splitter import split_documents
from ml.rag.vectorstore import get_vector_store


def profile_store_is_empty(
    embeddings: Embeddings | None = None,
    persist_directory: str | None = None,
) -> bool:
    """프로필 컬렉션에 저장된 문서가 없으면 True 반환"""
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
    """프로필 마크다운을 불러와 청크로 나누고, 벡터 스토어에 저장"""
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
    """벡터 스토어가 비어있을 때만 프로필을 저장하고, 저장이 실행되면 True 반환"""
    if not profile_store_is_empty(
        embeddings=embeddings,
        persist_directory=persist_directory,
    ):
        return False
    ingest_profile(embeddings=embeddings, persist_directory=persist_directory)
    return True

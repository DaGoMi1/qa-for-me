"""프로필 문서를 검색 가능한 청크로 분할"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
)


def split_documents(documents: list[Document]) -> list[Document]:
    """불러온 문서를 검색 가능한 청크로 분할"""
    return _SPLITTER.split_documents(documents)

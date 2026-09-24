"""Split profile documents into retrieval-sized chunks."""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
)


def split_documents(documents: list[Document]) -> list[Document]:
    """Break loaded documents into retrieval-sized chunks."""
    return _SPLITTER.split_documents(documents)

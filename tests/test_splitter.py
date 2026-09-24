"""Profile document splitter."""

from ml.rag.loader import load_profile_documents
from ml.rag.splitter import split_documents


def test_about_markdown_splits_into_chunks() -> None:
    """about.md becomes multiple chunks and keeps a project heading intact."""
    chunks = split_documents(load_profile_documents())
    assert len(chunks) >= 2
    assert any("movie-recommendation" in chunk.page_content for chunk in chunks)

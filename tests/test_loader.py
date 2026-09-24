"""Profile markdown loader."""

from ml.rag.loader import load_profile_documents


def test_about_markdown_is_loaded() -> None:
    """about.md is returned and its body includes the profile name."""
    documents = load_profile_documents()
    about = next(
        document
        for document in documents
        if document.metadata["source"].endswith("about.md")
    )
    assert "이다검" in about.page_content
    assert "movie-recommendation" in about.page_content

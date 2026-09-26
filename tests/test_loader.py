"""Profile markdown loader."""

from ml.rag.loader import load_profile_documents


def test_bio_and_projects_markdown_are_loaded() -> None:
    """bio.md and projects.md are loaded with expected profile facts."""
    documents = load_profile_documents()
    by_name = {
        document.metadata["source"].replace("\\", "/").split("/")[-1]: document
        for document in documents
    }
    assert "bio.md" in by_name
    assert "projects.md" in by_name
    assert "이다검" in by_name["bio.md"].page_content
    assert "국립한국해양대학교" in by_name["bio.md"].page_content
    assert "movie-recommendation" in by_name["projects.md"].page_content
    assert "qa-for-me" in by_name["projects.md"].page_content

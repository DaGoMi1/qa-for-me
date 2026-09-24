"""Entry point for loading profile markdown into the vector store."""

from ml.rag.ingest import ingest_profile


def main() -> None:
    """Load, split, and store the profile documents."""
    ingest_profile()


if __name__ == "__main__":
    main()

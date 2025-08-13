# Helpers for consistent storage paths
from pathlib import Path

STORAGE_ROOT = Path("storage")


def doc_root(document_id: str) -> Path:
    return STORAGE_ROOT / "documents" / document_id


def source_pdf_path(document_id: str) -> Path:
    return doc_root(document_id) / "source.pdf"


def index_dir(document_id: str) -> Path:
    return doc_root(document_id) / "index"

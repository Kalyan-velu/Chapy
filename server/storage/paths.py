# Helpers for consistent storage paths
from pathlib import Path

STORAGE_ROOT = Path("storage")


def doc_root(document_id: str) -> Path:
    return STORAGE_ROOT / "documents"


def source_pdf_path(document_id: str) -> Path:
    return doc_root(document_id) / f"{document_id}.pdf"


def index_dir(document_id: str) -> Path:
    return doc_root(document_id) / "index"

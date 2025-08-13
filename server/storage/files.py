from pathlib import Path
from typing import Dict, List, Optional
import json
import shutil

from fastapi import UploadFile

from .paths import STORAGE_ROOT, doc_root, source_pdf_path

CHUNK_SIZE = 1024 * 1024  # 1 MiB


def ensure_storage_root() -> None:
    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    (STORAGE_ROOT / "documents").mkdir(parents=True, exist_ok=True)


def _write_file_stream(upload: UploadFile, dest_path: Path, max_bytes: Optional[int] = None) -> int:
    total = 0
    with dest_path.open("wb") as out:
        while True:
            chunk = upload.file.read(CHUNK_SIZE)
            if not chunk:
                break
            out.write(chunk)
            total += len(chunk)
            if max_bytes is not None and total > max_bytes:
                # Stop early if exceeding budget
                raise ValueError("File too large")
    return total


def save_upload_as_source_pdf(document_id: str, upload: UploadFile, *, max_bytes: Optional[int] = None) -> Dict:
    """Save uploaded file to source.pdf under the document folder.

    Returns a metadata dict with name, size_bytes, and paths.
    """
    ensure_storage_root()
    root = doc_root(document_id)
    root.mkdir(parents=True, exist_ok=True)
    dest = source_pdf_path(document_id)

    # Reset file pointer to start
    try:
        upload.file.seek(0)
    except Exception:
        pass

    try:
        size = _write_file_stream(upload, dest, max_bytes=max_bytes)
    except Exception as e:
        # Cleanup partial file if exists
        if dest.exists():
            try:
                dest.unlink()
            except Exception:
                pass
        raise e

    meta = {
        "id": document_id,
        "name": getattr(upload, "filename", "source.pdf") or "source.pdf",
        "size_bytes": size,
        "status": "processing",
    }

    # Persist meta.json for quick listing
    (root / "meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def list_documents_meta() -> List[Dict]:
    ensure_storage_root()
    docs_dir = STORAGE_ROOT / "documents"
    items: List[Dict] = []
    if not docs_dir.exists():
        return items
    for child in docs_dir.iterdir():
        if not child.is_dir():
            continue
        meta_path = child / "meta.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
                # If index was built later, status may be updated by other services; keep as is
                items.append(meta)
            except Exception:
                # If meta is corrupted, skip
                continue
        else:
            # Fallback: infer minimal meta
            src = child / "source.pdf"
            if src.exists():
                items.append({
                    "id": child.name,
                    "name": "source.pdf",
                    "size_bytes": src.stat().st_size,
                    "status": "processing",
                })
    return items


def delete_document_storage(document_id: str) -> bool:
    """Delete the entire document folder from storage."""
    root = doc_root(document_id)
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
        return True
    return False

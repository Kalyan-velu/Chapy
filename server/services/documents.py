from typing import Dict, List
from fastapi import UploadFile, HTTPException

from utils.idgen import new_id
from storage.files import save_upload_as_source_pdf, list_documents_meta


DEFAULT_MAX_UPLOAD_MB = 200


def create_document_from_upload(upload: UploadFile, max_upload_mb: int = DEFAULT_MAX_UPLOAD_MB) -> Dict:
    """Create a new document, save uploaded file to storage, and return metadata.
    Raises HTTPException for validation issues.
    """
    # Basic content type / extension checks
    filename = upload.filename or "file.pdf"
    content_type = getattr(upload, "content_type", "application/octet-stream")
    if not (filename.lower().endswith(".pdf") or content_type in ("application/pdf",)):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    document_id = new_id()
    max_bytes = max_upload_mb * 1024 * 1024
    try:
        meta = save_upload_as_source_pdf(document_id, upload, max_bytes=max_bytes)
    except ValueError as ve:
        # File too large
        raise HTTPException(status_code=413, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save file") from e

    return meta


def list_documents() -> List[Dict]:
    return list_documents_meta()

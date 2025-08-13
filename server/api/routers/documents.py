from fastapi import APIRouter, UploadFile, File
from services.documents import create_document_from_upload, list_documents as list_documents_service

router = APIRouter(prefix="/api/documents", tags=["documents"]) 


@router.get("")
async def list_documents():
    return {"items": list_documents_service()}

# Also support trailing slash to avoid confusion between /api/documents and /api/documents/
@router.get("/")
async def list_documents_trailing():
    return {"items": list_documents_service()}


@router.post("")
async def upload_document(file: UploadFile = File(...)):
    meta = create_document_from_upload(file)
    # Return minimal create response
    return {"document_id": meta["id"], "status": meta.get("status", "processing")}

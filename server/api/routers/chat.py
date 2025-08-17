from fastapi import APIRouter

from llm.rag import get_index, document_indexes,get_query_engine

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.get("/health")
async def chat_health():
    return {"status": "ok"}

@router.get("/create/{doc_id}")
async def create_chat(doc_id:str):
    document_indexes[doc_id] = get_index(doc_id)
    return {"message": "Chat Created"}

@router.get("/{doc_id}")
async def chat(doc_id:str,msg:str):
    query_engine=get_query_engine(doc_id)
    return query_engine.query(msg)
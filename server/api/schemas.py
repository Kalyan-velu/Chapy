from pydantic import BaseModel
from typing import List, Literal, Optional

class Document(BaseModel):
    id: str
    name: str
    size_bytes: int
    status: Literal["processing", "ready", "failed"]

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    document_id: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = None
    top_k: Optional[int] = None
    temperature: Optional[float] = None
    token_budget: Optional[int] = None

class Citation(BaseModel):
    page: int
    node_id: str
    score: float

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]

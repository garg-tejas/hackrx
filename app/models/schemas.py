from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field

class QueryRequest(BaseModel):
    documents: str = Field(..., description="URL to the document blob")
    questions: List[str] = Field(..., description="List of questions to answer")

class QueryResponse(BaseModel):
    answers: List[str] = Field(..., description="List of answers corresponding to questions")
    explanations: Optional[List[str]] = Field(None, description="Explanation for each answer")
    confidence_scores: Optional[List[float]] = Field(None, description="Confidence score for each answer")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Source citations for each answer")

class DocumentChunk(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

class ProcessingResult(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None 
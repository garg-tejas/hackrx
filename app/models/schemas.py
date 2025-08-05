from typing import List
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    documents: str = Field(..., description="URL to the document blob")
    questions: List[str] = Field(..., description="List of questions to answer")

class QueryResponse(BaseModel):
    answers: List[str] = Field(..., description="List of answers corresponding to questions") 
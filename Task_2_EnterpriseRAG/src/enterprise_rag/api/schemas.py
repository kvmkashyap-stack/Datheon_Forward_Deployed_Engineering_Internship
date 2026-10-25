
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    user_id: str = Field(min_length=1)
    question: str = Field(min_length=1, max_length=4000)


class CitationResponse(BaseModel):
    source: str
    page: int = Field(ge=1)


class QueryResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
    retrieved_chunks: int = Field(ge=0)


class HealthResponse(BaseModel):
    status: str
    app_name: str


class UploadResponse(BaseModel):
    source: str
    pages_extracted: int = Field(ge=0)
    chunks_created: int = Field(ge=0)
    chunks_indexed: int = Field(ge=0)

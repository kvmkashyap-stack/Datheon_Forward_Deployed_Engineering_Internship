
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20_000)


class GenerateResponse(BaseModel):
    answer: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int

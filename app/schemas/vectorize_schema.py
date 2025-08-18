from pydantic import BaseModel, field_validator, Field
from typing import List

class VectorInput(BaseModel):
    text: List[str] = Field(..., description="List of input texts")

    @field_validator("text")
    def non_empty_texts(cls, v):
        if not v:
            raise ValueError("Text list must not be empty.")
        if not all(isinstance(item, str) and item.strip() for item in v):
            raise ValueError("All items in 'text' must be non-empty strings.")
        return v
    
class VectorResponse(BaseModel):
    vector: List[List[float]] = Field(..., description="Embedding vector")
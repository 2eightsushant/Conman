from pydantic import BaseModel, field_validator, Field
from typing import List

class RerankInput(BaseModel):
    text_list: List[List[str]] = Field(..., description="List of list of input texts")

    @field_validator("text_list")
    def non_empty_texts(cls, v):
        if not v:
            raise ValueError("Text list must not be empty.")
        for inner_list in v:
            if not isinstance(inner_list, list) or not all(isinstance(item, str) and item.strip() for item in inner_list):
                raise ValueError("All items in 'text_list' must be non-empty strings.")
        return v

class RerankResponse(BaseModel):
    score: float = Field(0.0, description="Semantic score from reranker model")
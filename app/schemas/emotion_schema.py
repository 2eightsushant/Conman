from pydantic import BaseModel, field_validator, Field
from typing import List

class EmotionInput(BaseModel):
    text: str = Field(..., description="Input texts")

    @field_validator("text")
    def non_empty_texts(cls, v):
        if not v:
            raise ValueError("Text must not be empty.")
        return v

class EmotionResponse(BaseModel):
    emotions: List[str] = Field(..., description="Top k emotions")
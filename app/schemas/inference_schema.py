from pydantic import BaseModel, field_validator, Field

class InferenceQuery(BaseModel):
    query: str = Field(..., description="Input query")

    @field_validator("query")
    def non_empty_texts(cls, v):
        if not v:
            raise ValueError("Query must not be empty.")
        return v

class InferenceResponse(BaseModel):
    emotions: str = Field(..., description="Generated response")
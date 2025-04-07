# app/schemas.py
from pydantic import BaseModel, Field, field_validator
from app.config import settings

class TextInput(BaseModel):
    """Request schema for text prediction."""
    text: str = Field(..., min_length=1, description="The text content to be analyzed.")

    @field_validator('text')
    @classmethod
    def text_must_not_be_empty(cls, value: str):
        if not value.strip():
            raise ValueError("Text cannot be empty or contain only whitespace.")
        return value

class PredictionOutput(BaseModel):
    """Response schema for text prediction."""
    softmax_score_class_0: float = Field(..., ge=0, le=1, description="Softmax probability score for class 0 (Human-written).")
    softmax_score_class_1: float = Field(..., ge=0, le=1, description="Softmax probability score for class 1 (AI-generated).")
    predicted_class: int = Field(..., description="Predicted class index (0 for Human, 1 for AI).")
    predicted_label: str = Field(..., description="Predicted class label ('Human-written' or 'AI-generated').")

class HealthCheck(BaseModel):
    """Response schema for health check."""
    message: str = "OK"
    service: str = settings.PROJECT_NAME
    status: str = "Running"
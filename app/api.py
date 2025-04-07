# app/api.py
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import TextInput, PredictionOutput, HealthCheck
from app.services import TextDetectionService, get_text_detection_service
from app.exceptions import ModelInferenceError

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Provides a basic health check endpoint."""
    return HealthCheck()


@router.post(
    "/predict",
    response_model=PredictionOutput,
    summary="Detect if text is AI-generated",
    tags=["Detection"]
)
async def detect_text(
    input_data: TextInput,
    service: TextDetectionService = Depends(get_text_detection_service)
) -> PredictionOutput:
    """Analyzes text to predict origin (Human vs AI)."""
    try:
        result = service.predict(input_data.text)
        return PredictionOutput(**result)
    except ModelInferenceError as e:
        # Let the global handler catch this HTTPException subclass
        raise e
    except Exception as e:
        # Catch unexpected errors during prediction request handling
        logger.exception("Unexpected error during prediction request.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred."
        )
# app/exceptions.py
from fastapi import HTTPException, status

class ModelInferenceError(HTTPException):
    """Indicates a failure during the model prediction phase."""
    def __init__(self, detail: str = "Model inference failed."):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class ModelLoadError(RuntimeError):
    """Indicates a failure during model or tokenizer loading."""
    def __init__(self, detail: str = "Failed to load the model or tokenizer."):
        super().__init__(detail)

class EmptyInputError(HTTPException):
    """Indicates invalid empty input provided by the client."""
    def __init__(self, detail: str = "Input text cannot be empty or contain only whitespace."):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
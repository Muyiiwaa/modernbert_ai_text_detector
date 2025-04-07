# app/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api import router as api_router
from app.config import settings
from app.logging_config import setup_logging
from app.services import get_text_detection_service
from app.exceptions import ModelLoadError

# Configure logging before application starts
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    logger.info("Application startup: Initializing resources...")
    try:
        # Eagerly initialize the service on startup to load the model
        get_text_detection_service()
        logger.info("Text detection service initialized.")
    except (ModelLoadError, RuntimeError) as e:
         # Critical failure if model cannot be loaded on startup
         logger.critical(f"Fatal error during startup: {e}", exc_info=True)
         # Raising error here might stop server startup, depending on deployment
         raise RuntimeError(f"Service initialization failed: {e}") from e

    yield # Application runs

    logger.info("Application shutdown.")
    # Add cleanup logic here if necessary


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    lifespan=lifespan
)


# --- Global Exception Handlers ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic validation errors."""
    logger.warning(f"Invalid request data: {exc.errors()}", extra={"errors": exc.errors()})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": exc.errors()},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handles exceptions raised via FastAPI's HTTPException."""
    # This will also catch our custom exceptions like ModelInferenceError
    logger.warning(f"HTTP Exception occurred: Status={exc.status_code}, Detail='{exc.detail}'")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handles any uncaught exceptions."""
    logger.exception(f"Unhandled exception during request to {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )

# --- Router Inclusion ---
app.include_router(api_router, prefix=settings.API_PREFIX)

# --- Root Endpoint ---
@app.get("/", summary="API Root", tags=["Root"], include_in_schema=False)
async def root():
    """Provides a simple root endpoint."""
    return {"message": f"{settings.PROJECT_NAME} is running."}
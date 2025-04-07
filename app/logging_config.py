# app/logging_config.py
import logging
import sys

from pythonjsonlogger import jsonlogger
from app.config import settings

def setup_logging():
    """Configures root logger and uvicorn loggers with JSON formatting."""
    log_level = logging.getLevelName(settings.LOG_LEVEL.upper())
    json_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s"
    )
    json_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    # Prevent adding duplicate handlers on reloads
    if not root_logger.handlers:
        root_logger.setLevel(log_level)
        root_logger.addHandler(json_handler)

        uvicorn_access_logger = logging.getLogger("uvicorn.access")
        uvicorn_access_logger.handlers = [json_handler]
        uvicorn_access_logger.propagate = False

        uvicorn_error_logger = logging.getLogger("uvicorn.error")
        uvicorn_error_logger.propagate = True # Propagate errors to root logger

        transformers_logger = logging.getLogger("transformers")
        transformers_logger.setLevel(logging.WARNING) # Reduce transformers verbosity
        transformers_logger.propagate = True

        logging.info(f"Logging configured with level: {settings.LOG_LEVEL}")
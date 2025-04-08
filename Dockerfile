# Stage 1: Build stage - Install dependencies
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /opt/app

# Install build dependencies if needed (e.g., for packages with C extensions)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential && rm -rf /var/lib/apt/lists/*
# Note: Torch CPU wheels usually don't require build-essential, uncomment if needed.

# Upgrade pip and install dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --wheel-dir /opt/app/wheels -r requirements.txt


# Stage 2: Final stage - Setup runtime environment
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set default values for runtime, can be overridden
ENV LOG_LEVEL="INFO"
ENV API_PREFIX="/api/v1"
ENV PROJECT_NAME="AI Text Detection API"
ENV MODEL_NAME="muyiiwaa/ai_detect_modernbert" 
ENV MODEL_MAX_LENGTH=512
ENV WORKERS=4 

# Set working directory
WORKDIR /opt/app

# Create a non-privileged user to run the application
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

# Install runtime dependencies (OS level if needed)
# Example: RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*
# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies from wheels built in the previous stage
COPY --from=builder /opt/app/wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* && \
    rm -rf /wheels # Clean up wheels after installation

# Copy application code into the container
# Ensure correct ownership for the non-root user
COPY --chown=appuser:appgroup ./app ./app

# Change ownership of the working directory to the app user
RUN chown -R appuser:appgroup /opt/app

# Switch to the non-privileged user
USER appuser

# Expose the port the application runs on
EXPOSE 8000

# Define healthcheck
# Uses the /api/v1/health endpoint defined in api.py
# Adjust the path if your API_PREFIX or health endpoint changes
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000${API_PREFIX}/health || exit 1

# Define the command to run the application using uvicorn
# Uses the WORKERS environment variable for concurrency
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "${WORKERS}"]
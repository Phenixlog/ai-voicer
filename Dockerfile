# Théoria API - Production Dockerfile
# Multi-stage build for optimized production image
# Uses Python 3.11 slim for balance of size and compatibility

# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM python:3.11-slim AS builder

# Security: Run as non-root
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Stage 2: Production
# ============================================================================
FROM python:3.11-slim AS production

# Security labels
LABEL maintainer="Théoria Team <team@theoria.app>"
LABEL org.opencontainers.image.title="Théoria API"
LABEL org.opencontainers.image.description="AI Voice Dictation API"
LABEL org.opencontainers.image.version="0.1.0"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY --chown=appuser:appgroup src/ ./src/
COPY --chown=appuser:appgroup run_api.py .

# Create logs directory
RUN mkdir -p /app/logs && chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Health check (Railway uses dynamic PORT)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sh -c "curl -f http://localhost:${PORT:-8000}/health || exit 1"

# Expose port
EXPOSE 8000

# Run the application with uvicorn
# Using single worker in container (scaling via orchestration)
CMD ["python", "run_api.py"]

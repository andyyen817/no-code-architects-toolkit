# ZEABUR Production Dockerfile - SIMPLIFIED
# No-Code Architects Toolkit - Fixed for Deployment

FROM python:3.11-slim

# Install essential system dependencies only
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements_zeabur.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_zeabur.txt

# Install Gunicorn separately
RUN pip install --no-cache-dir gunicorn==21.2.0

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/output/audio && \
    mkdir -p /app/output/videos && \
    mkdir -p /app/output/subtitles && \
    mkdir -p /app/temp

# Set proper permissions
RUN chmod -R 755 /app/output && \
    chmod -R 755 /app/temp

# Environment variables for production
ENV API_KEY=production-api-key-2024
ENV LOCAL_STORAGE_PATH=/app/output
ENV DEBUG=false
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Create simple health check endpoint test
RUN echo '#!/bin/bash\ncurl -f http://localhost:8080/health || exit 1' > /app/health_check.sh && \
    chmod +x /app/health_check.sh

# Health check - simplified
HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/health_check.sh

# Expose port
EXPOSE 8080

# Simple startup command - use Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "300", "--worker-class", "sync", "--keep-alive", "2", "app:app"]
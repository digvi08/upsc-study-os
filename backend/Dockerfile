FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libpq-dev \
    gcc \
    file \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (better Docker caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Debug information
RUN echo "========== APP CONTENTS ==========" && \
    ls -lah /app && \
    echo "" && \
    echo "========== START.SH ==========" && \
    cat /app/start.sh && \
    echo "" && \
    echo "========== FILE INFO ==========" && \
    file /app/start.sh && \
    echo "" && \
    echo "========== PERMISSIONS ==========" && \
    chmod +x /app/start.sh && \
    ls -l /app/start.sh

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Start application using sh directly
CMD ["/bin/sh", "/app/start.sh"]
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create non-root user
RUN useradd --create-home --shell /bin/bash hackrx && \
    chown -R hackrx:hackrx /app

# Expose port
EXPOSE 8000

# Default command (Railway will override this)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
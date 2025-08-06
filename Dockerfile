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
COPY tests/ ./tests/
COPY env.example ./
COPY railway_start.py ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash hackrx && \
    chown -R hackrx:hackrx /app

# Switch to non-root user
USER hackrx

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "railway_start.py"]
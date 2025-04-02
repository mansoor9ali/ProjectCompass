FROM python:3.9-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . ./dashboard/
COPY requirements-api.txt .

# Create data directory
RUN mkdir -p data/storage

# Install Python dependencies for API only
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-api.txt

# Expose the API port
EXPOSE 8000

# Start the API server
CMD ["python", "-m", "dashboard.server"]

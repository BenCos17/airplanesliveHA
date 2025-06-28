FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY run.py .

# Create non-root user but don't switch to it yet (Home Assistant will handle permissions)
RUN useradd -r -s /bin/false appuser

# The s6-overlay system will handle service startup
CMD ["/init"]
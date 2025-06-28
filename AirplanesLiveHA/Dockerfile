FROM ghcr.io/hassio-addons/base:14.0.0

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    python3-dev \
    py3-pip

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY run.py .

# Copy s6 service files
COPY rootfs/ /

# Set permissions
RUN chmod a+x /etc/services.d/airplanes_live_api/run
RUN chmod a+x /etc/services.d/airplanes_live_api/finish
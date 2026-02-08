FROM ghcr.io/hassio-addons/base:18.1.1

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    python3-dev \
    py3-pip \
    && rm -rf /var/cache/apk/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with security best practices
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY run.py .

# Set addon version at build time for runtime access
ARG ADDON_VERSION=1.4.40
ENV ADDON_VERSION=${ADDON_VERSION}

# Copy s6 service files
COPY rootfs/ /

# Set permissions for s6 services
RUN chmod a+x /etc/services.d/airplanes_live_api/run && \
    chmod a+x /etc/services.d/airplanes_live_api/finish

# Health check: ensure Python process is running and supervised
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f "/app/run.py" >/dev/null || exit 1
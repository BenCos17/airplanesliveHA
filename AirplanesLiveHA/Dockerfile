FROM ghcr.io/hassio-addons/base:14.0.0

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
    pip3 install --no-cache-dir -r requirements.txt && \
    pip3 cache purge

# Copy application files
COPY run.py .

# Copy s6 service files
COPY rootfs/ /

# Set permissions
RUN chmod a+x /etc/services.d/airplanes_live_api/run && \
    chmod a+x /etc/services.d/airplanes_live_api/finish

# Create non-root user for better security
RUN adduser -D -s /bin/sh -u 1000 airplanes && \
    chown -R airplanes:airplanes /app

# Switch to non-root user
USER airplanes

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ps aux | grep run.py || exit 1
# The Infiltrator - Docker Container
# Research Automation Framework for Browser Fingerprinting Studies

FROM ubuntu:22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Core utilities
    python3.10 \
    python3-pip \
    curl \
    wget \
    git \
    vim \
    net-tools \
    iproute2 \
    iptables \
    openssl \
    tzdata \
    # libfaketime for clock drift simulation
    faketime \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --no-cache-dir \
    playwright==1.40.0 \
    requests==2.31.0 \
    asyncio \
    python-socks[asyncio]

# Install Playwright browsers (Chromium)
RUN playwright install chromium
RUN playwright install-deps chromium

# Create application directories
RUN mkdir -p /app/infiltrator
RUN mkdir -p /tmp/infiltrator_logs
RUN mkdir -p /usr/local/bin

# Copy Infiltrator scripts
COPY entrypoint.py /app/infiltrator/
COPY identity_sync.py /usr/local/bin/identity_sync.py
COPY network_mask.sh /usr/local/bin/network_mask.sh
COPY webrtc_killswitch.js /app/infiltrator/
COPY kinematic_mouse.py /app/infiltrator/
COPY temporal_entropy.py /app/infiltrator/
COPY reading_mimicry.py /app/infiltrator/

# Make scripts executable
RUN chmod +x /app/infiltrator/entrypoint.py
RUN chmod +x /usr/local/bin/identity_sync.py
RUN chmod +x /usr/local/bin/network_mask.sh

# Set working directory
WORKDIR /app/infiltrator

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/infiltrator

# Network capabilities for iptables and interface manipulation
# Note: Container must be run with --cap-add=NET_ADMIN
# Docker run command: docker run --cap-add=NET_ADMIN --privileged infiltrator

# Entrypoint
CMD ["python3", "/app/infiltrator/entrypoint.py"]

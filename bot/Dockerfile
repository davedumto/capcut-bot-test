FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install ALL system dependencies for both Chromium AND Firefox
# Plus virtual display support for maximum browser compatibility
RUN apt-get update && apt-get install -y \
    # Basic utilities
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    procps \
    # Virtual display support (critical for VPS)
    xvfb \
    x11vnc \
    fluxbox \
    # Playwright/Chromium dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libxshmfence1 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxss1 \
    # Firefox-specific dependencies
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    # Fonts - comprehensive font support
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-unifont \
    fonts-dejavu-core \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install BOTH Chromium and Firefox browsers for maximum compatibility
RUN playwright install chromium firefox

# Create virtual display startup script
RUN echo '#!/bin/bash\n\
echo "Starting virtual display for browser automation..."\n\
# Kill any existing X processes\n\
pkill Xvfb || true\n\
pkill x11vnc || true\n\
pkill fluxbox || true\n\
# Start virtual display\n\
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &\n\
export DISPLAY=:99\n\
# Start window manager\n\
fluxbox &\n\
# Give display time to initialize\n\
sleep 2\n\
echo "Virtual display ready on :99"\n\
# Execute the main command\n\
exec "$@"' > /app/start-with-display.sh

# Make startup script executable
RUN chmod +x /app/start-with-display.sh

# Copy application code
COPY . .

# Set environment variables for virtual display operation
ENV HEADLESS=true
ENV DISPLAY=:99
# Disable GPU acceleration (causes issues in Docker)
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV GALLIUM_DRIVER=softpipe
# Firefox-specific optimizations for Docker
ENV MOZ_HEADLESS=1
ENV MOZ_DISABLE_GPU_SANDBOX=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application with virtual display support
CMD ["/app/start-with-display.sh", "python", "app.py"]
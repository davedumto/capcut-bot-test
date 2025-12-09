FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install ALL system dependencies required by Playwright/Chromium
# Including fonts that Playwright --with-deps tries to install
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    ca-certificates \
    # Playwright required dependencies
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
    # Fonts - using correct package names for Debian
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-unifont \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright chromium browser only (no --with-deps since we installed deps above)
RUN playwright install chromium

# Copy application code
COPY . .

# Set environment variables for headless operation
ENV HEADLESS=true
ENV DISPLAY=:99

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "app.py"]
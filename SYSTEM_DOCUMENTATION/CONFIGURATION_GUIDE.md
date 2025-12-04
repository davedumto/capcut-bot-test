# CapCut Account Sharing System - Configuration Guide

## Configuration Overview

The system uses environment variables and configuration files to manage settings across three services. This guide covers all configuration options and their proper setup.

---

## Environment Variables

### Backend Service Configuration (.env)

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/capcut_db

# Service URLs
BOT_SERVICE_URL=http://localhost:5001
FRONTEND_URL=http://localhost:3000

# Security
SECRET_KEY=d0jHLe60pCHdQMd_JTfTJkWR5XOPsghB1EGtgO78Vsk

# Email Configuration
GMAIL_USER=daevid621@gmail.com
GMAIL_APP_PASSWORD=vrecwdtlranpytll

# Environment
ENVIRONMENT=development  # development, staging, production
```

#### Database URL Format
```bash
# PostgreSQL connection string format
DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/[database_name]

# Examples
DATABASE_URL=postgresql://user:password@localhost:5432/capcut_db           # Local
DATABASE_URL=postgresql://user:secure_pass@db.example.com:5432/capcut_db  # Remote
DATABASE_URL=postgresql://user:pass@postgres:5432/capcut_db               # Docker
```

### Bot Service Configuration (.env)

```bash
# CapCut Account Credentials
CAPCUT_EMAIL=daevid621@gmail.com
CAPCUT_PASSWORD=Doomsday2022

# Gmail Credentials for IMAP
GMAIL_EMAIL=daevid621@gmail.com
GMAIL_APP_PASSWORD=vrecwdtlranpytll

# IMAP Configuration
IMAP_HOST=imap.gmail.com
IMAP_PORT=993

# Bot Behavior
ENVIRONMENT=development
HEADLESS=false          # true for production, false for debugging
DEBUG=true              # false for production
```

#### Browser Configuration
```bash
# Development settings (visual debugging)
HEADLESS=false
DEBUG=true
BROWSER_TIMEOUT=30000

# Production settings (performance optimized)
HEADLESS=true
DEBUG=false
BROWSER_TIMEOUT=10000
```

### Frontend Service Configuration (.env.local)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Development settings
NEXT_PUBLIC_ENVIRONMENT=development
```

---

## Configuration Classes

### Backend Configuration (Pydantic Settings)

```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Service URLs
    bot_service_url: str = "http://localhost:5001"
    frontend_url: str = "http://localhost:3000"
    
    # Security
    secret_key: str
    
    # Email
    gmail_user: str
    gmail_app_password: str
    
    # Environment
    environment: str = "development"
    
    # Scheduler Settings
    scheduler_timezone: str = "UTC"
    session_check_interval_minutes: int = 1
    password_cleanup_interval_minutes: int = 10
    
    # Security Settings
    cors_origins: list[str] = ["http://localhost:3000"]
    max_sessions_per_user: int = 1
    
    # Database Settings
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_recycle: int = 3600
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### Bot Service Configuration

```python
# bot/config.py
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # CapCut Account Credentials
    CAPCUT_EMAIL: str = os.getenv("CAPCUT_EMAIL", "daevid621@gmail.com")
    CAPCUT_PASSWORD: str = os.getenv("CAPCUT_PASSWORD", "Doomsday2022")
    
    # Gmail Credentials
    GMAIL_EMAIL: str = os.getenv("GMAIL_EMAIL", "daevid621@gmail.com")
    GMAIL_APP_PASSWORD: str = os.getenv("GMAIL_APP_PASSWORD", "")
    
    # IMAP Configuration
    IMAP_HOST: str = os.getenv("IMAP_HOST", "imap.gmail.com")
    IMAP_PORT: int = int(os.getenv("IMAP_PORT", "993"))
    
    # Bot Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Browser Settings
    BROWSER_TIMEOUT: int = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30000"))
    
    # Rate Limiting
    MAX_PASSWORD_RESETS_PER_HOUR: int = int(os.getenv("MAX_PASSWORD_RESETS_PER_HOUR", "5"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### Frontend Configuration (Next.js)

```typescript
// frontend/lib/config.ts
interface Config {
  apiUrl: string
  environment: string
  isProduction: boolean
  isDevelopment: boolean
}

const config: Config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT || 'development',
  isProduction: process.env.NODE_ENV === 'production',
  isDevelopment: process.env.NODE_ENV === 'development'
}

export default config
```

---

## Framework-Specific Configuration

### Next.js Configuration (next.config.js)

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // App Router configuration
  experimental: {
    serverActions: true
  },
  
  // Build optimization
  eslint: {
    ignoreDuringBuilds: false
  },
  typescript: {
    ignoreBuildErrors: false
  },
  
  // Image optimization
  images: {
    domains: ['localhost'],
    formats: ['image/webp', 'image/avif']
  },
  
  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY
  },
  
  // Redirects and rewrites
  async redirects() {
    return [
      {
        source: '/old-booking',
        destination: '/',
        permanent: true
      }
    ]
  },
  
  // Headers for security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          }
        ]
      }
    ]
  }
}

module.exports = nextConfig
```

### Tailwind CSS Configuration

```javascript
// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'pale': '#f5f2e8',      // Background
        'gold': '#d4a574',      // Primary accent
        'rough': '#4a3c28',     // Text headers
        'darknavy': '#2c3e50',  // Body text
        'bookedslot': '#e8e8e8' // Disabled state
      },
      boxShadow: {
        'warm': '0 4px 6px -1px rgba(212, 165, 116, 0.1), 0 2px 4px -1px rgba(212, 165, 116, 0.06)',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
```

---

## Database Configuration

### PostgreSQL Configuration

```sql
-- postgresql.conf settings for production
# Connection Settings
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Write Ahead Log
wal_buffers = 16MB
checkpoint_completion_target = 0.9
wal_level = replica

# Query Performance
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_destination = 'csvlog'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000  # Log slow queries
```

### Database Connection Pool

```python
# backend/app/models/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.database_url,
    
    # Connection pooling
    poolclass=QueuePool,
    pool_size=settings.db_pool_size,          # 20
    max_overflow=settings.db_max_overflow,    # 10
    pool_pre_ping=True,                       # Verify connections
    pool_recycle=settings.db_pool_recycle,    # 3600 seconds
    
    # Query optimization
    echo=False,                               # Don't log SQL in production
    future=True                               # Use SQLAlchemy 2.0 API
)
```

---

## Service Configuration

### FastAPI Configuration

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Application configuration
app = FastAPI(
    title="CapCut Sharing Backend",
    description="Backend API for CapCut account sharing platform",
    version="1.0.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
    openapi_url="/openapi.json" if settings.environment == "development" else None
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Request size limits
app.add_middleware(
    LimitUploadSizeMiddleware,
    max_upload_size=10 * 1024 * 1024  # 10MB
)
```

### APScheduler Configuration

```python
# backend/app/main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler(
    timezone=settings.scheduler_timezone,
    
    # Job store configuration
    jobstores={
        'default': {
            'type': 'sqlalchemy',
            'url': settings.database_url
        }
    },
    
    # Executor configuration
    executors={
        'default': {
            'type': 'threadpool',
            'max_workers': 20
        }
    },
    
    # Job defaults
    job_defaults={
        'coalesce': False,
        'max_instances': 3,
        'misfire_grace_time': 30
    }
)
```

---

## Environment-Specific Configurations

### Development Environment

```bash
# .env.development
DATABASE_URL=postgresql://user:password@localhost:5432/capcut_dev_db
BOT_SERVICE_URL=http://localhost:5001
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
HEADLESS=false
DEBUG=true
LOG_LEVEL=DEBUG
```

### Staging Environment

```bash
# .env.staging
DATABASE_URL=postgresql://user:staging_pass@staging-db:5432/capcut_staging_db
BOT_SERVICE_URL=http://staging-bot:5001
FRONTEND_URL=https://staging.capcutsharing.com
ENVIRONMENT=staging
HEADLESS=true
DEBUG=false
LOG_LEVEL=INFO
```

### Production Environment

```bash
# .env.production
DATABASE_URL=postgresql://user:production_pass@prod-db:5432/capcut_prod_db
BOT_SERVICE_URL=http://prod-bot:5001
FRONTEND_URL=https://capcutsharing.com
ENVIRONMENT=production
HEADLESS=true
DEBUG=false
LOG_LEVEL=WARNING
```

---

## Security Configuration

### SSL/TLS Configuration

```python
# For production deployment with SSL
import ssl

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('/path/to/cert.pem', '/path/to/key.pem')

# Run with SSL
uvicorn.run(app, host="0.0.0.0", port=443, ssl_context=ssl_context)
```

### Environment Variable Validation

```python
# backend/app/core/config.py
from pydantic import validator, Field

class Settings(BaseSettings):
    secret_key: str = Field(..., min_length=32)
    gmail_app_password: str = Field(..., min_length=16, max_length=16)
    
    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.startswith('postgresql://'):
            raise ValueError('Database URL must be PostgreSQL')
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('Environment must be development, staging, or production')
        return v
```

---

## Monitoring Configuration

### Logging Configuration

```python
# backend/app/core/logging.py
import logging
import sys
from pathlib import Path

def configure_logging(environment: str, log_level: str = "INFO"):
    """Configure application logging."""
    
    # Log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f"logs/capcut_{environment}.log")
        ]
    )
    
    # Configure specific loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)
    
    # Security logger
    security_logger = logging.getLogger("security")
    security_handler = logging.FileHandler("logs/security.log")
    security_handler.setFormatter(logging.Formatter(log_format))
    security_logger.addHandler(security_handler)
```

### Health Check Configuration

```python
# backend/app/api/health.py
from fastapi import APIRouter
import psutil
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.environment,
        "database": await check_database_health(),
        "scheduler": check_scheduler_health(),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }

@router.get("/health/database")
async def database_health():
    """Database-specific health check."""
    try:
        from app.models.database import engine
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {"status": "healthy", "connection": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

---

## Configuration Management Best Practices

### Environment Variable Hierarchy

1. **System Environment Variables** (highest priority)
2. **Docker Environment Files**
3. **Local .env files**
4. **Configuration class defaults** (lowest priority)

### Sensitive Data Management

```python
# Use environment variables for secrets
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

# Never commit secrets to version control
# Use .env.example for documentation
```

### Configuration Validation

```python
# Validate configuration on startup
def validate_configuration():
    """Validate all configuration settings."""
    errors = []
    
    # Check required environment variables
    required_vars = ["DATABASE_URL", "SECRET_KEY", "GMAIL_APP_PASSWORD"]
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Missing required environment variable: {var}")
    
    # Check database connectivity
    try:
        engine.execute("SELECT 1")
    except Exception as e:
        errors.append(f"Database connection failed: {e}")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
```

### Hot Configuration Reloading

```python
# Configuration that can be updated without restart
class DynamicSettings:
    def __init__(self):
        self._cache = {}
        self._cache_timeout = 60  # Cache for 60 seconds
    
    def get_setting(self, key: str, default=None):
        """Get setting with caching and database fallback."""
        now = time.time()
        cache_key = f"{key}_cached_at"
        
        if (cache_key not in self._cache or 
            now - self._cache[cache_key] > self._cache_timeout):
            
            # Refresh from database
            value = self._get_from_database(key) or default
            self._cache[key] = value
            self._cache[cache_key] = now
        
        return self._cache[key]
```
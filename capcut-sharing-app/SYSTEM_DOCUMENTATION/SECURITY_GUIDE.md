# CapCut Account Sharing System - Security Guide

## Security Overview

The CapCut Account Sharing System implements multiple layers of security to protect user data, credentials, and system integrity while maintaining a balance between security and usability for a public booking system.

---

## Authentication & Authorization

### Public Access Design
**No User Authentication Required**
- System designed as public booking platform
- Users only need name and email for reservations
- No user registration or login process
- Session management through time-based slots only

### Service-to-Service Communication
```python
# Backend to Bot Service Authentication
BOT_SERVICE_URL = "http://localhost:5001"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "CapCut-Backend-Service/1.0"
}

# Internal API calls with service identification
async def call_bot_service(endpoint: str, data: dict):
    response = await aiohttp.post(
        f"{BOT_SERVICE_URL}{endpoint}",
        json=data,
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=30)
    )
```

---

## Password Security

### CapCut Account Password Management
```python
# Strong password generation
def generate_strong_password(length: int = 14) -> str:
    """Generate cryptographically secure password."""
    chars = (
        string.ascii_lowercase +
        string.ascii_uppercase + 
        string.digits +
        "!@#$%^&*"
    )
    return ''.join(secrets.choice(chars) for _ in range(length))

# Password complexity requirements
- Minimum 12 characters
- Mixed case letters (a-z, A-Z) 
- Numbers (0-9)
- Special characters (!@#$%^&*)
- No dictionary words or patterns
```

### Database Password Storage
```python
# Bcrypt hashing for stored passwords
import bcrypt

def hash_password(plain_password: str) -> str:
    """Hash password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )
```

### Temporary Password Handling
```sql
-- Passwords table with automatic cleanup
CREATE TABLE passwords (
    id SERIAL PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,     -- Always stored hashed
    plain_password VARCHAR(255),             -- Temporary for email (1 hour max)
    session_id INTEGER REFERENCES sessions(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP                     -- Auto-cleanup timestamp
);

-- Automatic cleanup job (runs every 10 minutes)
DELETE FROM passwords 
WHERE expires_at < NOW() 
    OR (plain_password IS NOT NULL AND created_at < NOW() - INTERVAL '1 hour');
```

---

## Data Protection

### Personal Information Security
```python
# Minimal data collection
class BookingRequest(BaseModel):
    name: str = Field(..., max_length=255)         # Display name only
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')  # Validated email
    slot_id: str = Field(..., regex=r'^slot_\d{8}_\d{4}$')      # Validated slot format

# No storage of sensitive data
- No phone numbers or addresses
- No payment information  
- No identity documents
- No session recordings or screenshots
```

### Database Security
```python
# Connection security
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    # Connection encryption
    connect_args={
        "sslmode": "prefer",              # Use SSL when available
        "application_name": "capcut-backend"
    },
    # Connection pooling security
    pool_pre_ping=True,                   # Verify connections
    pool_recycle=3600,                    # Rotate connections hourly
    echo=False                            # Don't log SQL in production
)

# Database user permissions
GRANT CONNECT ON DATABASE capcut_db TO capcut_app;
GRANT USAGE ON SCHEMA public TO capcut_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON users, sessions, passwords, daily_logs TO capcut_app;
-- No admin privileges granted to application user
```

### Email Security
```python
# Gmail IMAP with App Passwords
IMAP_CONFIG = {
    "host": "imap.gmail.com",
    "port": 993,                          # SSL/TLS port
    "use_ssl": True,
    "username": settings.GMAIL_EMAIL,
    "password": settings.GMAIL_APP_PASSWORD  # Not regular password
}

# App Password requirements:
- 16-character generated password
- Specific to this application  
- Can be revoked independently
- Requires 2FA on Gmail account
```

---

## Browser Automation Security

### Stealth Techniques
```python
# Anti-detection browser configuration
browser = await playwright.chromium.launch(
    headless=True,                        # No GUI in production
    args=[
        '--no-first-run',
        '--disable-blink-features=AutomationControlled',  # Hide automation
        '--disable-web-security',                         # For testing only
        '--disable-features=VizDisplayCompositor',
        '--disable-extensions',
        '--no-sandbox',                                   # Container security
        '--disable-dev-shm-usage'
    ]
)

# Realistic user agent
context = await browser.new_context(
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    viewport={'width': 1920, 'height': 1080},
    locale='en-US',
    timezone_id='America/New_York'
)
```

### Session Isolation
```python
# Clean session for each password reset
async def reset_password_with_isolation():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        try:
            # Fresh context for each operation
            context = await browser.new_context()
            page = await context.new_page()
            
            # Clear any existing state
            await context.clear_cookies()
            await page.goto('about:blank')
            
            # Perform password reset
            result = await execute_password_reset(page)
            
        finally:
            # Always cleanup
            await browser.close()
            
    return result
```

### Credential Protection
```python
# Environment variable management
class Settings(BaseSettings):
    CAPCUT_EMAIL: str = Field(..., env="CAPCUT_EMAIL")
    CAPCUT_PASSWORD: str = Field(..., env="CAPCUT_PASSWORD")
    GMAIL_APP_PASSWORD: str = Field(..., env="GMAIL_APP_PASSWORD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
# Never log credentials
logger.info(f"Starting password reset for {email}")  # ✓ Safe
logger.info(f"Using password: {password}")           # ✗ NEVER DO THIS
```

---

## API Security

### Input Validation
```python
# Pydantic validation for all inputs
class BookingRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    slot_id: str = Field(..., regex=r'^slot_\d{8}_\d{4}$')
    
    @validator('name')
    def name_must_be_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z\s\-\.]+$', v):
            raise ValueError('Name contains invalid characters')
        return v.strip()
```

### CORS Configuration
```python
# Restricted CORS for frontend-only access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",          # Development frontend
        "https://yourdomain.com"          # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],        # Limited HTTP methods
    allow_headers=["Content-Type", "Authorization"]
)
```

### Rate Limiting
```python
# Bot service rate limiting
from asyncio import Semaphore
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests: int = 5, window_minutes: int = 15):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.requests = []
        self.semaphore = Semaphore(1)  # Only one password reset at a time
    
    async def allow_request(self) -> bool:
        async with self.semaphore:
            now = datetime.now()
            cutoff = now - timedelta(minutes=self.window_minutes)
            
            # Remove old requests
            self.requests = [req_time for req_time in self.requests if req_time > cutoff]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False

rate_limiter = RateLimiter()

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    if not await rate_limiter.allow_request():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    # Process request...
```

---

## Environment Security

### Production Configuration
```bash
# Secure environment variables
export CAPCUT_EMAIL="production-email@gmail.com"
export CAPCUT_PASSWORD="$(openssl rand -base64 32)"
export GMAIL_APP_PASSWORD="$(generate_app_password)"
export SECRET_KEY="$(openssl rand -base64 64)"
export DATABASE_URL="postgresql://user:$(openssl rand -base64 32)@localhost:5432/capcut_db"
export ENVIRONMENT="production"
export HEADLESS="true"
export DEBUG="false"
```

### Container Security
```dockerfile
# Dockerfile security best practices
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r capcut && useradd -r -g capcut capcut

# Install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER capcut
WORKDIR /app

# Copy application code
COPY --chown=capcut:capcut . .

# Run with restricted permissions
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Network Security
```bash
# Firewall configuration (production)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw deny 8000/tcp     # Block direct backend access
sudo ufw deny 5001/tcp     # Block direct bot access  
sudo ufw enable

# Application-level restrictions
# Backend: Only accept connections from frontend domain
# Bot service: Only accept connections from backend service
# Database: Only accept connections from application servers
```

---

## Monitoring & Incident Response

### Security Logging
```python
# Security event logging
import logging
from datetime import datetime

security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

def log_security_event(event_type: str, details: dict):
    """Log security-related events for monitoring."""
    security_logger.info(
        f"SECURITY_EVENT",
        extra={
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
    )

# Usage examples
log_security_event("password_reset_attempt", {"email": email, "success": True})
log_security_event("rate_limit_exceeded", {"ip_address": request.client.host})
log_security_event("invalid_session_access", {"session_id": session_id})
```

### Anomaly Detection
```python
# Monitor for unusual patterns
def detect_anomalies():
    # Multiple rapid bookings from same email
    recent_bookings = db.query(Session).filter(
        Session.created_at > datetime.now() - timedelta(minutes=10)
    ).group_by(Session.user_email).having(func.count() > 3).all()
    
    # Password reset failures
    failed_resets = get_recent_failed_password_resets()
    
    # Unusual booking patterns
    off_hours_bookings = db.query(Session).filter(
        extract('hour', Session.created_at).between(2, 5)
    ).all()
    
    if recent_bookings or failed_resets or off_hours_bookings:
        send_security_alert("Potential security anomaly detected")
```

### Incident Response
```python
# Automated security responses
async def security_incident_response(incident_type: str, severity: str):
    if severity == "high":
        # Immediate actions
        await disable_bot_service()
        await lock_database_writes()
        await notify_administrators()
        
    elif severity == "medium":
        # Enhanced monitoring
        await increase_logging_level()
        await enable_additional_monitoring()
        
    # Always log incident
    log_security_event("incident_response", {
        "type": incident_type,
        "severity": severity,
        "actions_taken": get_response_actions(severity)
    })
```

---

## Security Audit Checklist

### Regular Security Tasks

#### Weekly
- [ ] Review security logs for anomalies
- [ ] Check for failed password reset attempts
- [ ] Verify SSL certificate validity
- [ ] Monitor unusual booking patterns
- [ ] Check system resource usage

#### Monthly  
- [ ] Update all dependencies
- [ ] Rotate database passwords
- [ ] Review and update firewall rules
- [ ] Check for new security vulnerabilities
- [ ] Backup encryption key verification

#### Quarterly
- [ ] Full security audit of codebase
- [ ] Penetration testing (if required)
- [ ] Review and update security policies
- [ ] Test incident response procedures
- [ ] Security training for team members

### Vulnerability Assessment
```bash
# Regular security scans
# Python dependency scanning
pip-audit --desc --format=json --output vulnerabilities.json

# Docker image scanning  
docker scout cves capcut-backend:latest

# Network security scanning
nmap -sS -O localhost

# Web application scanning (production)
nikto -h https://yourdomain.com
```

---

## Emergency Procedures

### Security Breach Response
1. **Immediate Actions**
   - Isolate affected systems
   - Preserve logs for forensics
   - Disable compromised accounts
   - Notify stakeholders

2. **Assessment**
   - Determine scope of breach
   - Identify compromised data
   - Assess system integrity
   - Document timeline

3. **Recovery**
   - Patch vulnerabilities
   - Reset all credentials
   - Restore from clean backups
   - Implement additional monitoring

4. **Prevention**
   - Update security procedures
   - Enhance monitoring systems
   - Conduct security training
   - Review and test response plan

### Contact Information
```
Security Team: security@company.com
24/7 Hotline: +1-XXX-XXX-XXXX
Incident Report: security-incident@company.com
```
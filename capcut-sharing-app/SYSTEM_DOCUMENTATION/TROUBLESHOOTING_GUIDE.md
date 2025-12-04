# CapCut Account Sharing System - Troubleshooting Guide

## Quick Diagnostic Commands

### System Status Check
```bash
# Check all services are running
curl -s http://localhost:3000 > /dev/null && echo "✓ Frontend: Running" || echo "✗ Frontend: Down"
curl -s http://localhost:8000/health > /dev/null && echo "✓ Backend: Running" || echo "✗ Backend: Down"  
curl -s http://localhost:5001/health > /dev/null && echo "✓ Bot Service: Running" || echo "✗ Bot Service: Down"
psql -U user -d capcut_db -c "SELECT 1;" > /dev/null && echo "✓ Database: Connected" || echo "✗ Database: Connection failed"
```

### Service Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Bot service logs (if running with uvicorn)
docker logs capcut-bot -f

# Frontend logs (Next.js development)
cd frontend && npm run dev

# Database logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

---

## Common Issues

### 1. Port Conflicts

#### Problem: Port 5000 occupied (macOS ControlCenter)
```bash
# Check what's using port 5000
lsof -i :5000

# Expected output on macOS:
# COMMAND     PID USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
# ControlCe  1234 user    8u  IPv4 0x1234567890   0t0  TCP *:5000 (LISTEN)
```

**Solution:**
```bash
# Use alternative port for bot service
cd bot
python -m uvicorn app:app --host 0.0.0.0 --port 5001

# Update backend configuration
# In backend/.env:
BOT_SERVICE_URL=http://localhost:5001
```

#### Problem: Port 8000 occupied
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use alternative port
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 2. Database Connection Issues

#### Problem: Database "capcut_db" does not exist
```bash
# Error message:
# sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL:  database "capcut_db" does not exist
```

**Solution:**
```bash
# Create database
psql postgres -c "CREATE DATABASE capcut_db OWNER \"user\";"

# Verify creation
psql -U user -l | grep capcut_db
```

#### Problem: Role "user" does not exist
```bash
# Create PostgreSQL user
psql postgres -c "CREATE USER \"user\" WITH PASSWORD 'password';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE capcut_db TO \"user\";"
```

#### Problem: Connection refused to PostgreSQL
```bash
# Check PostgreSQL is running
brew services list | grep postgresql
# or
sudo systemctl status postgresql

# Start PostgreSQL
brew services start postgresql
# or  
sudo systemctl start postgresql

# Check connection
psql -U user -d capcut_db -c "SELECT 1;"
```

### 3. Python Import Errors

#### Problem: ModuleNotFoundError for pydantic_settings
```bash
# Error: ModuleNotFoundError: No module named 'pydantic_settings'
```

**Solution:**
```bash
# Install correct package
pip install pydantic-settings

# Update imports in code
# Change: from pydantic import BaseSettings
# To: from pydantic_settings import BaseSettings
```

#### Problem: Import error for bot services
```bash
# Error: ModuleNotFoundError: No module named 'services.gmail_handler'
```

**Solution:**
```bash
# Check current directory and module structure
cd bot
ls -la services/

# Ensure __init__.py files exist
touch services/__init__.py

# Run from correct directory
python -m uvicorn app:app --host 0.0.0.0 --port 5001
```

### 4. Gmail/IMAP Issues

#### Problem: Gmail authentication failed
```bash
# Error: imaplib.IMAP4.error: b'[AUTHENTICATIONFAILED] Invalid credentials (Failure)'
```

**Solution:**
```bash
# 1. Enable 2-Factor Authentication on Gmail
# 2. Generate App Password:
#    Google Account → Security → App passwords → Mail → Other
# 3. Use 16-character app password (not regular password)

# Test IMAP connection
python3 -c "
import imaplib
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('your-email@gmail.com', 'your-16-char-app-password')
print('✓ IMAP connection successful')
mail.logout()
"
```

#### Problem: No CapCut emails found
```bash
# Error: No emails found matching CapCut criteria
```

**Solution:**
```bash
# Check email search manually
python3 -c "
import imaplib
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('email@gmail.com', 'app_password')
mail.select('inbox')
status, messages = mail.search(None, 'ALL')
print(f'Total emails: {len(messages[0].split())}')

# Search for CapCut emails
status, capcut_messages = mail.search(None, 'FROM', 'capcut')
print(f'CapCut emails: {len(capcut_messages[0].split()) if capcut_messages[0] else 0}')
mail.logout()
"
```

### 5. Browser Automation Issues

#### Problem: Playwright browser not installed
```bash
# Error: playwright._impl._api_types.Error: Executable doesn't exist
```

**Solution:**
```bash
# Install browsers
cd bot
playwright install chromium

# Verify installation
playwright install --dry-run
```

#### Problem: Browser launch failed in production
```bash
# Error: Failed to launch browser in headless mode
```

**Solution:**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxss1 \
    libasound2

# Test browser launch
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    print('✓ Browser launch successful')
    browser.close()
"
```

#### Problem: CapCut website elements not found
```bash
# Error: TimeoutError: Timeout 10000ms exceeded waiting for selector
```

**Solution:**
```bash
# Debug with visual browser
# In bot/.env:
HEADLESS=false
DEBUG=true

# Run bot service and watch browser actions
# Check if CapCut website layout changed
# Update selectors in services/capcut_bot.py if needed
```

### 6. Frontend Issues

#### Problem: API connection refused
```bash
# Error: TypeError: Failed to fetch
```

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS configuration in backend
# In backend/app/main.py, verify:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Problem: Next.js build failed
```bash
# Error: Type error: Cannot find module '@/components/...'
```

**Solution:**
```bash
# Check tsconfig.json paths configuration
cat frontend/tsconfig.json

# Verify file structure matches imports
ls -la frontend/components/
ls -la frontend/lib/

# Clear Next.js cache
cd frontend
rm -rf .next
npm run build
```

### 7. Scheduler Issues

#### Problem: Background jobs not running
```bash
# Check scheduler status
curl http://localhost:8000/scheduler/status
```

**Solution:**
```bash
# Verify APScheduler configuration
# Check logs for scheduler startup messages:
# "✅ Scheduler started - running session management and password cleanup jobs"

# Manual job trigger for testing
python3 -c "
import asyncio
from app.scheduler.jobs import session_start_job
asyncio.run(session_start_job())
"
```

#### Problem: Sessions not transitioning status
```bash
# Check sessions table
psql -U user -d capcut_db -c "
SELECT id, status, start_time, end_time, created_at 
FROM sessions 
ORDER BY created_at DESC 
LIMIT 5;
"
```

**Solution:**
```bash
# Manually update session status for testing
psql -U user -d capcut_db -c "
UPDATE sessions 
SET status = 'active' 
WHERE start_time <= NOW() AND status = 'pending';
"

# Check scheduler jobs are registered
curl http://localhost:8000/scheduler/status | jq '.jobs'
```

---

## Performance Issues

### 1. Slow API Responses

#### Diagnosis:
```bash
# Test API response times
time curl http://localhost:8000/api/slots

# Check database query performance
psql -U user -d capcut_db -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

#### Solutions:
```bash
# Add database indexes
psql -U user -d capcut_db -c "
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
"

# Monitor slow queries
# In postgresql.conf:
log_min_duration_statement = 1000
```

### 2. High Memory Usage

#### Diagnosis:
```bash
# Check memory usage
ps aux | grep -E "(python|node)" | sort -k 4 -nr

# Check database connections
psql -U user -d capcut_db -c "
SELECT count(*) as connections, state 
FROM pg_stat_activity 
GROUP BY state;
"
```

#### Solutions:
```bash
# Optimize database connection pool
# In backend/app/models/database.py:
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # Reduce from 20
    max_overflow=5,      # Reduce from 10
    pool_recycle=1800    # Reduce from 3600
)

# Monitor browser memory in bot service
# Consider browser restart after N operations
```

### 3. Bot Service Timeouts

#### Diagnosis:
```bash
# Check bot service response times
time curl -X POST http://localhost:5001/bot/reset-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

#### Solutions:
```bash
# Increase timeouts in bot service
# In bot/config.py:
BROWSER_TIMEOUT=60000      # Increase from 30000
PAGE_LOAD_TIMEOUT=45000    # Increase from 30000

# Optimize browser performance
# In bot/services/capcut_bot.py:
browser = await p.chromium.launch(
    headless=True,
    args=['--disable-dev-shm-usage', '--no-sandbox']
)
```

---

## Environment-Specific Issues

### Development Environment

#### Problem: Hot reloading not working
```bash
# Next.js frontend
# Check if files are being watched
cd frontend
npm run dev -- --turbo

# FastAPI backend
# Use --reload flag
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Problem: CORS errors in development
```bash
# Check browser console for CORS errors
# Update backend CORS configuration:
allow_origins=["http://localhost:3000", "http://localhost:3001"]
```

### Production Environment

#### Problem: Environment variables not loaded
```bash
# Check environment variables are set
printenv | grep -E "(DATABASE_URL|SECRET_KEY|GMAIL_APP_PASSWORD)"

# Load from file if needed
set -a; source .env; set +a
```

#### Problem: SSL certificate issues
```bash
# Check certificate validity
openssl x509 -in /path/to/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

### Docker Environment

#### Problem: Container networking issues
```bash
# Check container connectivity
docker network ls
docker network inspect capcut_default

# Test inter-container communication
docker exec capcut-backend curl http://capcut-bot:5001/health
```

#### Problem: Volume mount issues
```bash
# Check volume mounts
docker inspect capcut-backend | jq '.[0].Mounts'

# Verify file permissions
docker exec capcut-backend ls -la /app/logs
```

---

## Diagnostic Scripts

### Complete System Health Check
```bash
#!/bin/bash
# health_check.sh

echo "=== CapCut System Health Check ==="

# Check services
services=("frontend:3000" "backend:8000" "bot:5001")
for service in "${services[@]}"; do
    name=${service%:*}
    port=${service#*:}
    if curl -s "http://localhost:$port" > /dev/null 2>&1; then
        echo "✓ $name (port $port): Running"
    else
        echo "✗ $name (port $port): Down"
    fi
done

# Check database
if psql -U user -d capcut_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✓ Database: Connected"
else
    echo "✗ Database: Connection failed"
fi

# Check scheduler
if curl -s "http://localhost:8000/scheduler/status" | jq -e '.scheduler_running == true' > /dev/null 2>&1; then
    echo "✓ Scheduler: Running"
else
    echo "✗ Scheduler: Not running"
fi

echo "=== End Health Check ==="
```

### Database Diagnostic Script
```python
#!/usr/bin/env python3
# db_diagnostic.py

import psycopg2
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/capcut_db")

def check_database():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Check tables exist
            tables = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")).fetchall()
            print(f"✓ Tables found: {[t[0] for t in tables]}")
            
            # Check record counts
            for table in ['users', 'sessions', 'passwords', 'daily_logs']:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table};")).scalar()
                    print(f"✓ {table}: {result} records")
                except Exception as e:
                    print(f"✗ {table}: {e}")
            
            # Check recent activity
            recent_sessions = conn.execute(text(
                "SELECT COUNT(*) FROM sessions WHERE created_at > NOW() - INTERVAL '24 hours';"
            )).scalar()
            print(f"✓ Recent sessions (24h): {recent_sessions}")
            
    except Exception as e:
        print(f"✗ Database check failed: {e}")

if __name__ == "__main__":
    check_database()
```

### Log Analysis Script
```bash
#!/bin/bash
# analyze_logs.sh

echo "=== Recent Errors ==="
grep -r "ERROR\|CRITICAL" backend/logs/ | tail -20

echo "=== Password Reset Attempts ==="
grep "reset_password" backend/logs/* | tail -10

echo "=== Session Activity ==="
grep "session" backend/logs/* | grep -E "(created|started|ended)" | tail -10

echo "=== Database Queries ==="
grep "SQL" backend/logs/* | tail -5
```

---

## Getting Help

### Log Collection for Support
```bash
#!/bin/bash
# collect_logs.sh

mkdir -p support_logs/
cp backend/logs/*.log support_logs/ 2>/dev/null || echo "No backend logs found"
docker logs capcut-backend > support_logs/backend_docker.log 2>&1
docker logs capcut-bot > support_logs/bot_docker.log 2>&1
docker logs capcut-frontend > support_logs/frontend_docker.log 2>&1

# System information
uname -a > support_logs/system_info.txt
docker --version >> support_logs/system_info.txt
python3 --version >> support_logs/system_info.txt
node --version >> support_logs/system_info.txt

# Configuration (sanitized)
env | grep -E "ENVIRONMENT|HEADLESS|DEBUG" > support_logs/config.txt

echo "Logs collected in support_logs/ directory"
```

### Common Support Questions

1. **"The system is not booking sessions"**
   - Check: Database connection, scheduler status, session creation API
   - Run: `curl -X POST http://localhost:8000/api/bookings -H "Content-Type: application/json" -d '{"name":"Test","email":"test@example.com","slot_id":"slot_20241123_1400"}'`

2. **"Password reset is failing"**
   - Check: Gmail IMAP credentials, CapCut account credentials, browser automation
   - Run: Bot service in non-headless mode for visual debugging

3. **"Frontend shows no available slots"**
   - Check: Backend API connectivity, slot generation logic, CORS configuration
   - Run: `curl http://localhost:8000/api/slots`

4. **"Sessions are not starting automatically"**
   - Check: Scheduler status, session status in database, bot service connectivity
   - Run: `curl http://localhost:8000/scheduler/status`

### Emergency Recovery

#### Reset System State
```bash
# Stop all services
docker-compose down

# Reset database
psql -U user -d capcut_db -c "
TRUNCATE sessions, passwords, daily_logs CASCADE;
UPDATE users SET created_at = NOW();
"

# Restart services
docker-compose up -d

# Verify system health
./health_check.sh
```

#### Emergency Contact
- System Administrator: admin@company.com
- Database Administrator: dba@company.com  
- On-call Engineer: +1-XXX-XXX-XXXX
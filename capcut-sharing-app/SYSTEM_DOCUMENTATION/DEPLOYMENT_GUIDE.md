# CapCut Account Sharing System - Deployment Guide

## Prerequisites

### System Requirements
- **Operating System:** macOS, Linux, or Windows with WSL
- **Node.js:** Version 18+ with npm
- **Python:** Version 3.9+ with pip
- **PostgreSQL:** Version 12+ 
- **Browser:** Chrome/Chromium for Playwright automation
- **Email:** Gmail account with App Password enabled

### Required Accounts
- Gmail account for email processing
- CapCut Pro account for sharing
- PostgreSQL database instance

---

## Local Development Setup

### 1. Clone and Setup Project
```bash
# Clone the repository
git clone <repository-url>
cd capcut-sharing-app

# Create environment files
cp backend/.env.example backend/.env
cp bot/.env.example bot/.env
cp frontend/.env.local.example frontend/.env.local
```

### 2. Database Setup
```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database and user
psql postgres
CREATE DATABASE capcut_db;
CREATE USER "user" WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE capcut_db TO "user";
\q
```

### 3. Backend Service Setup
```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost:5432/capcut_db
BOT_SERVICE_URL=http://localhost:5001
FRONTEND_URL=http://localhost:3000
SECRET_KEY=d0jHLe60pCHdQMd_JTfTJkWR5XOPsghB1EGtgO78Vsk
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
ENVIRONMENT=development
EOF

# Start backend service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Bot Service Setup
```bash
cd ../bot

# Install Python dependencies  
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure environment variables
cat > .env << EOF
CAPCUT_EMAIL=your-capcut-email@gmail.com
CAPCUT_PASSWORD=your-capcut-password
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
ENVIRONMENT=development
HEADLESS=false
DEBUG=true
EOF

# Start bot service
python -m uvicorn app:app --host 0.0.0.0 --port 5001
```

### 5. Frontend Service Setup
```bash
cd ../frontend

# Install Node.js dependencies
npm install

# Configure environment variables
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Start frontend service
npm run dev
```

---

## Service Verification

### Check Service Status
```bash
# Backend health check
curl http://localhost:8000/health

# Bot service health check  
curl http://localhost:5001/health

# Frontend access
open http://localhost:3000
```

### Test Database Connection
```bash
# Verify tables created
psql -U user -d capcut_db -c "\dt"

# Should show: users, sessions, passwords, daily_logs
```

### Test API Endpoints
```bash
# Get available slots
curl http://localhost:8000/api/slots

# Check scheduler status
curl http://localhost:8000/scheduler/status

# Test bot service (requires valid credentials)
curl -X POST http://localhost:5001/bot/reset-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

---

## Production Deployment

### Docker Deployment

#### 1. Build Docker Images
```bash
# Backend image
cd backend
docker build -t capcut-backend .

# Bot service image
cd ../bot  
docker build -t capcut-bot .

# Frontend image
cd ../frontend
docker build -t capcut-frontend .
```

#### 2. Docker Compose Setup
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: capcut_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    image: capcut-backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/capcut_db
      BOT_SERVICE_URL: http://bot:5001
      FRONTEND_URL: http://localhost:3000
    depends_on:
      - postgres

  bot:
    image: capcut-bot
    ports:
      - "5001:5001"
    environment:
      CAPCUT_EMAIL: ${CAPCUT_EMAIL}
      CAPCUT_PASSWORD: ${CAPCUT_PASSWORD}
      GMAIL_EMAIL: ${GMAIL_EMAIL}
      GMAIL_APP_PASSWORD: ${GMAIL_APP_PASSWORD}
      HEADLESS: "true"

  frontend:
    image: capcut-frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000

volumes:
  postgres_data:
```

#### 3. Deploy with Docker Compose
```bash
# Create production environment file
cat > .env << EOF
CAPCUT_EMAIL=your-capcut-email@gmail.com
CAPCUT_PASSWORD=your-capcut-password
GMAIL_EMAIL=your-gmail@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
EOF

# Deploy all services
docker-compose up -d

# Check service status
docker-compose ps
docker-compose logs
```

---

## Environment Configuration

### Gmail App Password Setup
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password:
   - Google Account → Security → App passwords
   - Select "Mail" and "Other"
   - Copy 16-character password
3. Use this password in `GMAIL_APP_PASSWORD`

### CapCut Account Setup
1. Create CapCut Pro account
2. Verify email access for password reset
3. Use credentials in `CAPCUT_EMAIL` and `CAPCUT_PASSWORD`

### SSL/TLS Configuration (Production)
```bash
# Install certbot for SSL certificates
sudo apt-get install certbot

# Generate SSL certificates
sudo certbot certonly --standalone -d yourdomain.com

# Update nginx configuration
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```

---

## Monitoring and Maintenance

### Log Management
```bash
# Backend logs
tail -f backend/app.log

# Bot service logs  
tail -f bot/bot.log

# Frontend logs (development)
npm run dev 2>&1 | tee frontend.log

# Docker logs
docker-compose logs -f backend
docker-compose logs -f bot
```

### Database Maintenance
```bash
# Backup database
pg_dump -U user capcut_db > backup_$(date +%Y%m%d).sql

# Restore database
psql -U user capcut_db < backup_20241123.sql

# Clean old sessions (monthly)
psql -U user -d capcut_db -c "DELETE FROM sessions WHERE created_at < NOW() - INTERVAL '30 days';"
```

### Performance Monitoring
```bash
# Check service health endpoints
curl http://localhost:8000/health
curl http://localhost:5001/health

# Monitor scheduler jobs
curl http://localhost:8000/scheduler/status

# Database connection monitoring
psql -U user -d capcut_db -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using port 5000 (macOS ControlCenter)
lsof -i :5000

# Kill process using port
kill -9 $(lsof -ti:5000)

# Use alternative port for bot service
python -m uvicorn app:app --host 0.0.0.0 --port 5001
```

#### Database Connection Errors
```bash
# Test database connection
psql -U user -d capcut_db -c "SELECT 1;"

# Check if database exists
psql -U user -l | grep capcut_db

# Recreate database if needed
psql postgres -c "DROP DATABASE IF EXISTS capcut_db;"
psql postgres -c "CREATE DATABASE capcut_db OWNER \"user\";"
```

#### Gmail IMAP Issues
```bash
# Test IMAP connection
python3 -c "
import imaplib
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('your-email@gmail.com', 'your-app-password')
print('IMAP connection successful')
"
```

#### Playwright Browser Issues
```bash
# Reinstall browsers
playwright install --force chromium

# Check browser installation
playwright install --dry-run

# Test browser launch
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    print('Browser launch successful')
    browser.close()
"
```

### Performance Issues

#### High CPU Usage
- Enable headless mode: `HEADLESS=true`
- Reduce browser instances in bot service
- Optimize database queries with indexes
- Monitor scheduler job frequency

#### Memory Leaks
- Restart services daily with cron jobs
- Monitor Docker container memory usage
- Clean up expired passwords regularly
- Optimize database connection pooling

#### Slow API Responses
- Enable database query logging
- Add API response time monitoring
- Optimize slot generation algorithm
- Cache frequently accessed data

---

## Security Considerations

### Production Hardening
```bash
# Use strong passwords and secrets
SECRET_KEY=$(openssl rand -base64 32)

# Restrict database access
# Only allow backend service to connect

# Enable firewall rules
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw deny 8000   # Block direct backend access
sudo ufw deny 5001   # Block direct bot access
sudo ufw enable
```

### Regular Security Tasks
- Rotate database passwords monthly
- Update all dependencies regularly
- Monitor logs for suspicious activity
- Backup encryption keys securely
- Review API access patterns

### Data Privacy
- Auto-delete expired passwords
- Encrypt database backups
- Anonymize user data in logs
- Implement data retention policies
# CapCut Account Sharing System - Operations Quick Reference

## 🖥️ System Status (30-second check)

### Health Check Commands
```bash
# Quick system health
curl -s http://localhost:3000 && echo "✓ Frontend" || echo "✗ Frontend"
curl -s http://localhost:8000/health && echo "✓ Backend" || echo "✗ Backend"  
curl -s http://localhost:5001/health && echo "✓ Bot Service" || echo "✗ Bot Service"
psql -U user -d capcut_db -c "SELECT 1;" 2>/dev/null && echo "✓ Database" || echo "✗ Database"

# Detailed health
curl -s http://localhost:8000/scheduler/status | jq '.scheduler_running'
```

### Service Ports & URLs
- **Frontend**: http://localhost:3000 (Public)
- **Backend**: http://localhost:8000 (Internal API)
- **Bot Service**: http://localhost:5001 (Internal)
- **Database**: PostgreSQL port 5432 (Internal)

---

## 🔧 Service Management

### Start Services
```bash
# Development mode
cd frontend && npm run dev &
cd backend && python -m uvicorn app.main:app --reload --port 8000 &
cd bot && python -m uvicorn app:app --reload --port 5001 &

# Production mode
docker-compose up -d

# Or individually:
systemctl start capcut-frontend
systemctl start capcut-backend  
systemctl start capcut-bot
```

### Stop Services
```bash
# Development
pkill -f "npm run dev"
pkill -f "uvicorn.*8000"
pkill -f "uvicorn.*5001"

# Production
docker-compose down
systemctl stop capcut-{frontend,backend,bot}
```

### Restart Services
```bash
# Quick restart (development)
./restart_services.sh

# Production restart with zero downtime
docker-compose up -d --force-recreate
```

---

## 📊 Monitoring

### Log Locations
```bash
# Application logs
tail -f backend/logs/app.log
tail -f bot/logs/bot.log

# System logs
journalctl -u capcut-backend -f
journalctl -u capcut-bot -f

# Docker logs
docker-compose logs -f backend
docker-compose logs -f bot
```

### Key Metrics
```bash
# Active sessions
curl -s http://localhost:8000/api/sessions/active | jq

# Database connections
psql -U user -d capcut_db -c "SELECT count(*) FROM pg_stat_activity;"

# Recent bookings (last 24h)
psql -U user -d capcut_db -c "SELECT count(*) FROM sessions WHERE created_at > NOW() - INTERVAL '24 hours';"

# System resources
top -p $(pgrep -f "uvicorn\|npm")
df -h
free -m
```

### Performance Monitoring
```bash
# Response times
time curl http://localhost:8000/api/slots
time curl http://localhost:5001/health

# Database performance  
psql -U user -d capcut_db -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;"

# Error rates
grep -c "ERROR\|CRITICAL" backend/logs/app.log | tail -10
```

---

## 🚨 Troubleshooting

### Service Not Starting

#### Port Conflicts
```bash
# Check port usage
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5001  # Bot service
lsof -i :5432  # Database

# Kill blocking processes
sudo lsof -ti:8000 | xargs kill -9
```

#### Database Issues
```bash
# Database not accessible
sudo service postgresql status
sudo service postgresql start

# Wrong database/user
psql -l  # List databases
psql postgres -c "\du"  # List users

# Create missing database
psql postgres -c "CREATE DATABASE capcut_db OWNER \"user\";"
```

#### Permission Issues
```bash
# File permissions
chmod +x scripts/*.sh
chown -R appuser:appuser /app/

# Database permissions
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE capcut_db TO \"user\";"
```

### Service Errors

#### Backend API Errors
```bash
# Check database connectivity
python -c "from backend.app.models.database import engine; engine.execute('SELECT 1')"

# Verify environment variables
printenv | grep -E "DATABASE_URL|SECRET_KEY"

# Check CORS issues
curl -H "Origin: http://localhost:3000" http://localhost:8000/api/slots
```

#### Bot Service Issues
```bash
# Test browser installation
cd bot && python -c "from playwright.sync_api import sync_playwright; sync_playwright().chromium.launch()"

# Test IMAP connection
python -c "import imaplib; imaplib.IMAP4_SSL('imap.gmail.com').login('email', 'password')"

# Check credentials
grep -v "^#" bot/.env | grep -E "CAPCUT_EMAIL|GMAIL"
```

#### Frontend Issues
```bash
# Check API connectivity
curl -s http://localhost:8000/health || echo "Backend unreachable"

# Clear Next.js cache
cd frontend && rm -rf .next && npm run dev

# Check environment variables
grep NEXT_PUBLIC frontend/.env.local
```

---

## 📅 Scheduled Maintenance

### Daily Tasks (Automated)
```bash
# Log rotation
logrotate /etc/logrotate.d/capcut

# Database cleanup (expired passwords)
psql -U user -d capcut_db -c "DELETE FROM passwords WHERE expires_at < NOW() - INTERVAL '1 day';"

# Health check
./scripts/health_check.sh
```

### Weekly Tasks
```bash
# Database backup
pg_dump -U user capcut_db > backups/capcut_$(date +%Y%m%d).sql

# Clear old sessions (30+ days)
psql -U user -d capcut_db -c "DELETE FROM sessions WHERE created_at < NOW() - INTERVAL '30 days';"

# Update dependencies (test environment first)
cd frontend && npm audit fix
cd backend && pip list --outdated
```

### Monthly Tasks
```bash
# Security updates
apt update && apt upgrade
npm audit && npm audit fix

# Performance review
analyze_performance_logs.sh

# Capacity planning
check_disk_usage.sh
review_database_size.sh
```

---

## 🔒 Security Operations

### Certificate Management
```bash
# Check certificate expiry
openssl x509 -in /path/to/cert.pem -text -noout | grep "Not After"

# Renew certificates (Let's Encrypt)
certbot renew --dry-run
certbot renew
sudo systemctl reload nginx
```

### Access Control
```bash
# Review active sessions
psql -U user -d capcut_db -c "SELECT user_email, start_time, status FROM sessions WHERE status = 'active';"

# Check failed login attempts (if implemented)
grep "authentication failed" backend/logs/security.log

# Monitor unusual activity
analyze_access_patterns.sh
```

### Backup & Recovery
```bash
# Create full backup
./scripts/backup_system.sh

# Test restore procedure
./scripts/test_restore.sh

# Verify backup integrity
pg_restore --list backups/latest_backup.sql > /dev/null && echo "Backup valid"
```

---

## 📈 Capacity Management

### Database Monitoring
```bash
# Database size
psql -U user -d capcut_db -c "
SELECT pg_size_pretty(pg_database_size('capcut_db')) as db_size;
SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size 
FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Connection usage
psql -U user -d capcut_db -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

# Query performance
psql -U user -d capcut_db -c "SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### System Resources
```bash
# Disk usage
df -h
du -sh /var/lib/postgresql/
du -sh /app/logs/

# Memory usage
free -m
ps aux --sort=-%mem | head -10

# CPU usage
top -bn1 | grep "Cpu(s)"
iostat 1 3
```

### Scaling Decisions
```bash
# Current load metrics
./scripts/check_current_load.sh

# Growth trend analysis  
./scripts/analyze_growth_trends.sh

# Capacity recommendations
./scripts/capacity_planning.sh
```

---

## 🔄 Deployment Operations

### Pre-deployment Checks
```bash
# Code quality
cd frontend && npm run lint && npm run type-check
cd backend && flake8 app/ && mypy app/

# Tests
npm test
pytest

# Security scan
npm audit
safety check
```

### Deployment Steps
```bash
# 1. Backup current state
./scripts/pre_deploy_backup.sh

# 2. Deploy new version
git pull origin main
docker-compose build
docker-compose up -d

# 3. Verify deployment
./scripts/post_deploy_verification.sh

# 4. Rollback if needed
docker-compose down
docker-compose up -d --build capcut-backend:previous
```

### Post-deployment Verification
```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:5001/health

# Functional tests
./scripts/smoke_tests.sh

# Performance baseline
./scripts/performance_check.sh

# Monitor error logs
tail -f backend/logs/app.log | grep -i error
```

---

## 📞 Incident Response

### Severity Levels

#### P1 - Critical (15min response)
- All services down
- Database corruption
- Security breach
```bash
# Immediate actions
./scripts/emergency_stop.sh
./scripts/isolate_systems.sh  
./scripts/notify_team.sh
```

#### P2 - High (1hr response)  
- Single service down
- Performance degradation
- Password reset failures
```bash
# Investigation
./scripts/collect_logs.sh
./scripts/analyze_recent_changes.sh
```

#### P3 - Medium (4hr response)
- Minor functionality issues
- Non-critical errors
- User complaints
```bash
# Standard troubleshooting
./scripts/standard_diagnostics.sh
```

### Emergency Contacts
```bash
# Escalation chain
echo "Primary: DevOps Team (slack: #ops-alerts)"
echo "Secondary: Engineering Manager"
echo "Executive: CTO (for P1 only)"

# On-call rotation
curl -s http://internal-tools/on-call | jq '.current_engineer'
```

---

## 📋 Daily Operations Checklist

### Morning Check (5 minutes)
- [ ] All services healthy
- [ ] No critical errors in logs
- [ ] Database backup completed
- [ ] Disk space < 80%
- [ ] No failed password resets

### Business Hours Monitoring
- [ ] Response times < 2 seconds
- [ ] Active sessions working properly  
- [ ] New bookings processing correctly
- [ ] Email notifications sending

### End of Day
- [ ] Review error logs
- [ ] Check resource usage trends
- [ ] Verify backup integrity
- [ ] Update incident log if applicable

---

## 🛠️ Quick Fix Commands

### Restart Hung Service
```bash
# Backend restart
docker-compose restart backend

# Bot service restart  
docker-compose restart bot

# Database connection reset
docker-compose restart db
```

### Clear Cache/Temp Files
```bash
# Application cache
rm -rf backend/__pycache__/
rm -rf frontend/.next/

# Browser automation cache
rm -rf bot/browser_cache/
```

### Reset Test Data
```bash
# Clear test sessions
psql -U user -d capcut_db -c "DELETE FROM sessions WHERE user_email LIKE '%test%';"

# Reset demo accounts
./scripts/reset_demo_data.sh
```

### Emergency User Commands  
```bash
# Cancel user session
psql -U user -d capcut_db -c "UPDATE sessions SET status = 'cancelled' WHERE user_email = 'user@example.com' AND status = 'active';"

# Force password rotation
curl -X POST http://localhost:5001/bot/reset-password -H "Content-Type: application/json" -d '{"email":"capcut-account@gmail.com"}'
```
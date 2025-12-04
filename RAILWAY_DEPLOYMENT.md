# CapCut Sharing Platform - Railway Deployment Guide

## 🚂 Railway Multi-Service Deployment

### Recommended: Deploy as 3 Separate Services

Railway works best with single-service deployments. Deploy each service separately:

#### 1. Database Setup
1. **Create PostgreSQL Database** in Railway dashboard
2. **Note the DATABASE_URL** from the database service

#### 2. Backend Service
1. **Create new Railway service** from GitHub
2. **Root Directory**: Set to `backend`
3. **Add Environment Variables**:
```bash
DATABASE_URL=postgresql://postgres:password@host:5432/railway
BOT_SERVICE_URL=https://your-bot-service.railway.app
FRONTEND_URL=https://your-frontend.railway.app
SECRET_KEY=your_secret_key_generate_new_one
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
ENVIRONMENT=production
```

#### 3. Bot Service  
1. **Create new Railway service** from GitHub
2. **Root Directory**: Set to `bot`
3. **Add Environment Variables**:
```bash
CAPCUT_EMAIL=your-capcut-email@gmail.com
CAPCUT_PASSWORD=your_capcut_password
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
ENVIRONMENT=production
HEADLESS=true
PORT=5000
```

#### 4. Frontend Service
1. **Create new Railway service** from GitHub  
2. **Root Directory**: Set to `frontend`
3. **Add Environment Variables**:
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NODE_ENV=production
```

## 📁 Repository Structure

```
capcut-bot-test/           ← Git root (deploy from here)
├── backend/               ← Backend service (Root: backend)
├── bot/                   ← Bot service (Root: bot)
├── frontend/              ← Frontend service (Root: frontend)
├── docker-compose.yml     ← For local development
├── init.sql               ← Database init script
└── ...
```

## 🔧 Environment Variables Checklist

### Required for all services:
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `CAPCUT_EMAIL` - CapCut account email
- [ ] `CAPCUT_PASSWORD` - CapCut account password
- [ ] `GMAIL_EMAIL` - Gmail account for bot
- [ ] `GMAIL_APP_PASSWORD` - Gmail app password (16 chars)
- [ ] `SECRET_KEY` - Backend security key
- [ ] `ENVIRONMENT` - Set to "production"
- [ ] `HEADLESS` - Set to "true"

### Service URLs (set after deployment):
- [ ] `FRONTEND_URL` - Frontend service URL
- [ ] `BOT_SERVICE_URL` - Bot service URL  
- [ ] `NEXT_PUBLIC_API_URL` - Backend API URL

## 📊 Expected Costs

With Railway's $5 monthly credit:
- **Database**: ~$2/month
- **Backend**: ~$1/month  
- **Bot**: ~$2-3/month (Playwright memory usage)
- **Frontend**: ~$0.50/month

**Total**: ~$5.50/month (only $0.50 overage)

## 🚀 Quick Deployment Steps

1. Push your code to GitHub
2. Create Railway account and connect GitHub
3. Add PostgreSQL database addon
4. Create **3 separate services** pointing to:
   - `backend` folder
   - `bot` folder
   - `frontend` folder
5. Configure environment variables for each
6. Deploy and test!

## 🔍 Troubleshooting

### Build Failures:
- Ensure root directory is set correctly for each service
- Check all environment variables are configured
- Verify GitHub repository permissions

### Runtime Issues:
- Monitor service logs in Railway dashboard
- Check database connection strings
- Verify service URLs are correctly set

### Bot Memory Issues:
- Bot service needs 1-2GB RAM for Playwright
- Monitor usage in Railway metrics
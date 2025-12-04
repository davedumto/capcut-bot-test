# CapCut Account Sharing System - Developer Quick Reference

## 🚀 Development Setup (5 minutes)

### Prerequisites
```bash
# Install dependencies
brew install postgresql node python3
npm install -g @playwright/test
```

### Quick Start
```bash
# 1. Setup database
psql postgres -c "CREATE DATABASE capcut_db OWNER \"user\";"

# 2. Backend (Terminal 1)
cd backend
pip install -r requirements.txt
cp .env.example .env  # Edit with your settings
python -m uvicorn app.main:app --reload --port 8000

# 3. Bot Service (Terminal 2)  
cd bot
pip install -r requirements.txt
playwright install chromium
cp .env.example .env  # Edit with your settings
python -m uvicorn app:app --port 5001

# 4. Frontend (Terminal 3)
cd frontend
npm install
npm run dev

# 5. Verify setup
curl http://localhost:8000/health
curl http://localhost:5001/health  
open http://localhost:3000
```

---

## 📁 Key File Locations

### Backend (FastAPI)
```
backend/app/
├── main.py              # App entry point + CORS
├── api/                 # API endpoints
│   ├── slots.py        # GET /api/slots
│   ├── bookings.py     # POST /api/bookings
│   └── sessions.py     # GET /api/sessions/*
├── models/
│   ├── database.py     # SQLAlchemy models
│   └── schemas.py      # Pydantic schemas
├── services/           # Business logic
├── scheduler/jobs.py   # Background tasks
└── core/config.py      # Settings management
```

### Frontend (Next.js)
```
frontend/
├── app/page.tsx        # Main booking flow
├── components/
│   ├── BookingForm.tsx     # User input form
│   ├── SlotSelector.tsx    # Time slot grid
│   └── ConfirmationModal.tsx
├── lib/
│   ├── api.ts              # Backend API client
│   └── utils.ts            # Helper functions
└── tailwind.config.js      # Custom colors
```

### Bot Service (FastAPI)
```
bot/
├── app.py                      # Entry point
├── routes/reset_password.py    # POST /bot/reset-password
├── services/
│   ├── capcut_bot.py          # 11-step password reset
│   ├── gmail_handler.py       # Email processing
│   └── password_generator.py  # Secure passwords
└── config.py                  # Settings
```

---

## 🔧 Common Development Tasks

### Database Operations
```bash
# Connect to database
psql -U user -d capcut_db

# Reset database
psql -U user -d capcut_db -c "TRUNCATE sessions, passwords CASCADE;"

# Check tables
\dt

# View recent sessions
SELECT id, status, start_time, user_email FROM sessions ORDER BY created_at DESC LIMIT 5;
```

### API Testing
```bash
# Get available slots
curl http://localhost:8000/api/slots | jq

# Create booking
curl -X POST http://localhost:8000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","slot_id":"slot_20241123_1400"}'

# Test bot service
curl -X POST http://localhost:5001/bot/reset-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","new_password":"TestPass123!"}'

# Check scheduler
curl http://localhost:8000/scheduler/status | jq
```

### Frontend Development
```bash
# Start with hot reloading
npm run dev

# Build for production  
npm run build

# Run tests
npm test

# Type checking
npm run type-check
```

---

## 🐛 Debugging

### Backend Debugging
```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message here")

# Database query debugging
echo=True  # In create_engine() for SQL logging
```

### Frontend Debugging  
```typescript
// API call debugging
console.log('API Request:', { endpoint, options })
console.log('API Response:', response)

// Component state debugging
useEffect(() => {
  console.log('State changed:', { step, userDetails })
}, [step, userDetails])
```

### Bot Service Debugging
```python
# Visual debugging
HEADLESS=false  # In .env

# Screenshot debugging
await page.screenshot(path=f"debug_{step}.png")

# Console logging
page.on("console", lambda msg: print(f"Browser: {msg.text}"))
```

---

## 📦 Environment Variables

### Required Settings
```bash
# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/capcut_db
BOT_SERVICE_URL=http://localhost:5001
SECRET_KEY=your-secret-key
GMAIL_APP_PASSWORD=16-char-app-password

# Bot Service  
CAPCUT_EMAIL=your-capcut-email@gmail.com
CAPCUT_PASSWORD=your-capcut-password
GMAIL_EMAIL=your-gmail@gmail.com
GMAIL_APP_PASSWORD=16-char-app-password
HEADLESS=false  # true for production

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest -v                    # Run all tests
pytest tests/test_api/ -v    # API tests only
pytest -k test_booking -v    # Specific test
```

### Frontend Tests
```bash
cd frontend
npm test                     # Run tests
npm test -- --watch         # Watch mode
npm test -- --coverage      # With coverage
```

### Integration Testing
```bash
# Manual end-to-end test
./test_integration.sh

# Or step by step:
curl http://localhost:8000/api/slots
# Book a slot, check session created
# Verify session details
```

---

## 🔄 Code Patterns

### Adding New API Endpoint
```python
# 1. Add route (backend/app/api/new_feature.py)
@router.post("/new-feature")
async def create_feature(request: NewFeatureRequest):
    # Implementation
    return {"success": True, "data": result}

# 2. Add to main.py
app.include_router(new_feature.router, prefix="/api")

# 3. Add frontend API call (frontend/lib/api.ts)
export const createFeature = (data: NewFeatureRequest) => 
  apiClient.request('/api/new-feature', { method: 'POST', body: JSON.stringify(data) })
```

### Database Model Changes
```python
# 1. Update model (backend/app/models/database.py)
class NewModel(Base):
    __tablename__ = "new_table"
    id = Column(Integer, primary_key=True)

# 2. Create tables
python -c "from app.models.database import create_tables; create_tables()"
```

### Adding Frontend Component
```typescript
// 1. Create component (frontend/components/NewComponent.tsx)
interface NewComponentProps { /* props */ }
export default function NewComponent({ }: NewComponentProps) { /* JSX */ }

// 2. Add to page (frontend/app/page.tsx)
import NewComponent from '@/components/NewComponent'
```

---

## 🚨 Common Issues & Fixes

### Port Conflicts
```bash
# Port 5000 (macOS ControlCenter)
lsof -i :5000 && echo "Port occupied - use 5001"

# Kill processes
lsof -ti:8000 | xargs kill -9
```

### Database Issues
```bash
# Database doesn't exist
psql postgres -c "CREATE DATABASE capcut_db OWNER \"user\";"

# Connection refused
brew services start postgresql
```

### Import Errors
```bash
# pydantic_settings not found
pip install pydantic-settings

# Playwright browser missing
playwright install chromium
```

### CORS Issues
```python
# Update backend CORS (backend/app/main.py)
allow_origins=["http://localhost:3000", "http://localhost:3001"]
```

---

## 📚 Key Dependencies

### Backend
- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM  
- **APScheduler**: Background jobs
- **Pydantic**: Data validation
- **psycopg2**: PostgreSQL driver

### Frontend  
- **Next.js 15**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **React 19**: UI library

### Bot Service
- **Playwright**: Browser automation
- **IMAP**: Email processing
- **FastAPI**: Web framework
- **Pydantic**: Configuration

---

## 🔗 Useful Commands

### Git Workflow
```bash
git checkout -b feature/new-feature
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

### Docker Commands
```bash
docker-compose up -d          # Start all services
docker-compose logs backend   # View logs
docker-compose down           # Stop services
docker-compose build          # Rebuild images
```

### Production Deploy
```bash
# Build
npm run build                 # Frontend
docker build -t capcut-app .  # Services

# Deploy
git push origin main          # Auto-deploy
docker-compose up -d          # Manual deploy
```
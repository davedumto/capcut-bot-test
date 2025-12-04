# CapCut Account Sharing System - Developer Guide

## Development Environment Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+ and pip
- PostgreSQL 12+
- Git for version control
- VS Code or similar IDE

### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd capcut-sharing-app

# Setup development environment
./setup.sh  # Creates databases, installs dependencies
```

### IDE Configuration

#### VS Code Extensions
- **Python**: ms-python.python
- **TypeScript**: ms-vscode.vscode-typescript-next
- **Tailwind CSS**: bradlc.vscode-tailwindcss
- **PostgreSQL**: ms-ossdata.vscode-postgresql
- **REST Client**: humao.rest-client

#### Settings.json
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "typescript.preferences.importModuleSpecifier": "relative",
  "tailwindCSS.includeLanguages": {
    "typescript": "javascript",
    "typescriptreact": "javascript"
  }
}
```

---

## Project Structure

### Root Directory
```
capcut-sharing-app/
├── frontend/           # Next.js application
├── backend/           # FastAPI application  
├── bot/              # Bot service for automation
├── SYSTEM_DOCUMENTATION/  # Generated documentation
├── setup.sh          # Environment setup script
├── test_capcut.py    # Integration test script
└── README.md         # Project overview
```

### Frontend Structure (Next.js)
```
frontend/
├── app/
│   ├── layout.tsx    # Root layout with providers
│   ├── page.tsx      # Main booking flow
│   ├── globals.css   # Tailwind + custom styles
│   └── favicon.ico
├── components/
│   ├── BookingForm.tsx      # User input form
│   ├── SlotSelector.tsx     # Time slot grid
│   ├── ConfirmationModal.tsx # Booking success
│   └── Header.tsx           # Page header
├── lib/
│   ├── api.ts        # Backend API client
│   └── utils.ts      # Utility functions
├── package.json      # Dependencies and scripts
├── tailwind.config.js # Style configuration
├── next.config.js    # Next.js settings
└── tsconfig.json     # TypeScript config
```

### Backend Structure (FastAPI)
```
backend/
├── app/
│   ├── main.py       # FastAPI application entry
│   ├── api/          # API route handlers
│   │   ├── slots.py      # Time slot endpoints
│   │   ├── bookings.py   # Booking endpoints
│   │   └── sessions.py   # Session management
│   ├── models/       # Database models
│   │   ├── database.py   # SQLAlchemy models
│   │   └── schemas.py    # Pydantic schemas
│   ├── services/     # Business logic
│   │   ├── password_service.py
│   │   ├── email_service.py
│   │   └── bot_service.py
│   ├── scheduler/    # Background jobs
│   │   └── jobs.py
│   └── core/         # Configuration
│       ├── config.py
│       └── security.py
├── requirements.txt  # Python dependencies
└── Dockerfile       # Container configuration
```

### Bot Service Structure
```
bot/
├── app.py           # FastAPI entry point
├── routes/          # API endpoints
│   └── reset_password.py
├── services/        # Core automation
│   ├── capcut_bot.py      # Browser automation
│   ├── gmail_handler.py   # Email processing
│   └── password_generator.py
├── config.py        # Settings management
├── requirements.txt
└── Dockerfile
```

---

## Development Workflow

### Branch Strategy
```bash
# Main branches
main                 # Production-ready code
develop             # Integration branch

# Feature branches
feature/slot-booking     # New booking features
feature/email-notifications  # Email system
bugfix/password-rotation    # Bug fixes
hotfix/critical-issue      # Production fixes
```

### Code Standards

#### Python (PEP 8)
```python
# Use type hints
async def create_booking(user_data: BookingRequest) -> BookingResponse:
    pass

# Docstrings for all functions
def generate_slots() -> List[TimeSlot]:
    """Generate 30-minute time slots for booking.
    
    Returns:
        List of TimeSlot objects with availability status
    """
    pass

# Use descriptive variable names
session_start_time = datetime.now()
user_email_address = request.email
```

#### TypeScript/React
```typescript
// Use interfaces for props
interface SlotSelectorProps {
  userDetails: { name: string; email: string }
  onBookingComplete: (sessionId: string) => void
}

// Use async/await for API calls
const handleBooking = async (slotId: string) => {
  try {
    const response = await createBooking({ name, email, slot_id: slotId })
    onBookingComplete(response.session_id)
  } catch (error) {
    setError(error.message)
  }
}

// Use descriptive component names
export default function BookingConfirmationModal({ ... }) { }
```

### Git Commit Standards
```bash
# Conventional Commits format
feat: add email notification system
fix: resolve password rotation timing issue  
docs: update API documentation
refactor: improve slot generation algorithm
test: add integration tests for booking flow
chore: update dependencies

# Example commit
git commit -m "feat: implement slot booking with real-time availability

- Add SlotSelector component with time-based grouping
- Integrate booking API with proper error handling  
- Add loading states and confirmation flow
- Update API client with type safety

Fixes #123"
```

---

## API Development

### Adding New Endpoints

#### 1. Backend Route (FastAPI)
```python
# app/api/new_feature.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.schemas import NewFeatureRequest, NewFeatureResponse

router = APIRouter()

@router.post("/new-feature", response_model=NewFeatureResponse)
async def create_new_feature(
    request: NewFeatureRequest,
    db: Session = Depends(get_db)
):
    try:
        # Implementation here
        return NewFeatureResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2. Database Model
```python
# app/models/database.py
class NewFeature(Base):
    __tablename__ = "new_features"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="features")
```

#### 3. Pydantic Schema
```python
# app/models/schemas.py
class NewFeatureRequest(BaseModel):
    name: str
    description: Optional[str] = None

class NewFeatureResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str
```

#### 4. Frontend API Client
```typescript
// lib/api.ts
interface NewFeatureRequest {
  name: string
  description?: string
}

interface NewFeatureResponse {
  success: boolean
  data: any
  message: string
}

async createNewFeature(request: NewFeatureRequest): Promise<NewFeatureResponse> {
  return this.request<NewFeatureResponse>('/api/new-feature', {
    method: 'POST',
    body: JSON.stringify(request)
  })
}

export const createNewFeature = apiClient.createNewFeature.bind(apiClient)
```

### Database Migrations

#### Creating Migrations
```python
# Create migration file: migrations/001_add_new_feature.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.models.database import Base

def upgrade(engine):
    # Create new table
    Base.metadata.create_all(bind=engine, tables=[NewFeature.__table__])

def downgrade(engine):
    # Drop table
    NewFeature.__table__.drop(engine)
```

#### Running Migrations
```bash
# Apply migrations
python -c "
from app.models.database import engine
from migrations.001_add_new_feature import upgrade
upgrade(engine)
"
```

---

## Frontend Development

### Component Development Pattern

#### 1. Component Structure
```typescript
'use client'
import { useState, useEffect } from 'react'

interface ComponentProps {
  // Props interface
}

export default function ComponentName({ }: ComponentProps) {
  // State declarations
  const [data, setData] = useState<DataType[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Effects
  useEffect(() => {
    fetchData()
  }, [])

  // Event handlers
  const handleAction = async () => {
    try {
      setLoading(true)
      // API call or logic
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Render logic
  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage error={error} />

  return (
    <div className="component-container">
      {/* Component JSX */}
    </div>
  )
}
```

#### 2. Styling with Tailwind
```typescript
// Use custom color scheme
<div className="bg-pale border-2 border-gold/20 rounded-lg p-6 shadow-warm">
  <h2 className="text-xl font-semibold text-rough mb-4">
    Title
  </h2>
  <p className="text-darknavy">
    Description text
  </p>
</div>

// Responsive design
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map(item => (
    <div key={item.id} className="p-4 bg-pale rounded-lg">
      {item.name}
    </div>
  ))}
</div>
```

### State Management Patterns

#### Simple State (useState)
```typescript
// Form state
const [formData, setFormData] = useState({
  name: '',
  email: ''
})

const updateFormData = (field: string, value: string) => {
  setFormData(prev => ({ ...prev, [field]: value }))
}
```

#### API State Management
```typescript
// API state pattern
const [apiState, setApiState] = useState({
  data: null,
  loading: false,
  error: null
})

const fetchData = async () => {
  setApiState(prev => ({ ...prev, loading: true, error: null }))
  try {
    const data = await apiCall()
    setApiState({ data, loading: false, error: null })
  } catch (error) {
    setApiState(prev => ({ ...prev, loading: false, error: error.message }))
  }
}
```

---

## Bot Service Development

### Browser Automation Patterns

#### Page Interaction
```python
async def interact_with_page(page):
    # Wait for elements
    await page.wait_for_selector('input[type="email"]', timeout=10000)
    
    # Fill forms safely
    email_input = await page.locator('input[type="email"]')
    await email_input.fill('')  # Clear first
    await email_input.fill(email)
    
    # Click with retry
    for attempt in range(3):
        try:
            await page.click('button[type="submit"]')
            break
        except TimeoutError:
            if attempt == 2:
                raise
            await asyncio.sleep(1)
```

#### Error Handling
```python
async def safe_automation_step(page, action_name: str, action_func):
    """Execute automation step with error handling."""
    try:
        logger.info(f"Starting: {action_name}")
        result = await action_func()
        logger.info(f"Completed: {action_name}")
        return result
    except TimeoutError:
        logger.error(f"Timeout in {action_name}")
        raise
    except Exception as e:
        logger.error(f"Error in {action_name}: {str(e)}")
        raise
```

### Email Processing

#### IMAP Operations
```python
def process_emails_safely(mail_handler: GmailHandler):
    """Process emails with proper error handling."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            reset_info = mail_handler.fetch_reset_email()
            if reset_info:
                return reset_info
        except Exception as e:
            logger.warning(f"Email fetch attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(5)
    return None
```

---

## Testing

### Unit Tests

#### Backend Tests
```python
# tests/test_booking_service.py
import pytest
from app.services.booking_service import create_booking
from app.models.schemas import BookingRequest

@pytest.fixture
def sample_booking_request():
    return BookingRequest(
        name="Test User",
        email="test@example.com",
        slot_id="slot_20241123_1400"
    )

async def test_create_booking_success(sample_booking_request):
    result = await create_booking(sample_booking_request)
    assert result.success == True
    assert "sess_" in result.session_id
```

#### Frontend Tests
```typescript
// __tests__/components/BookingForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import BookingForm from '@/components/BookingForm'

describe('BookingForm', () => {
  test('submits form with valid data', async () => {
    const mockSubmit = jest.fn()
    render(<BookingForm onSubmit={mockSubmit} />)
    
    fireEvent.change(screen.getByLabelText('Name'), {
      target: { value: 'Test User' }
    })
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@example.com' }
    })
    fireEvent.click(screen.getByText('Show Available Slots'))
    
    expect(mockSubmit).toHaveBeenCalledWith({
      name: 'Test User',
      email: 'test@example.com'
    })
  })
})
```

### Integration Tests
```python
# tests/test_integration.py
async def test_full_booking_flow():
    # Create booking
    booking_response = await client.post("/api/bookings", json={
        "name": "Integration Test",
        "email": "integration@test.com",
        "slot_id": "slot_20241123_1500"
    })
    assert booking_response.status_code == 200
    
    # Verify session created
    session_id = booking_response.json()["session_id"]
    session_response = await client.get(f"/api/sessions/{session_id}")
    assert session_response.status_code == 200
```

---

## Debugging

### Backend Debugging
```python
# Add detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Debug database queries
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    print(f"SQL: {statement}")
    print(f"Parameters: {parameters}")
```

### Frontend Debugging
```typescript
// Debug API calls
const apiClient = {
  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    console.log('API Request:', { endpoint, options })
    const response = await fetch(url, config)
    console.log('API Response:', { status: response.status, url })
    return response.json()
  }
}

// Debug component state
useEffect(() => {
  console.log('Component state changed:', { step, userDetails, bookingData })
}, [step, userDetails, bookingData])
```

### Bot Service Debugging
```python
# Visual debugging mode
await browser.launch(headless=False, slow_mo=1000)

# Screenshot capture
await page.screenshot(path=f"debug_{step_name}.png")

# Console logging
page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
```

---

## Performance Optimization

### Backend Optimization
```python
# Database query optimization
@router.get("/api/slots")
async def get_slots(db: Session = Depends(get_db)):
    # Use efficient queries
    slots = db.query(Session).options(
        joinedload(Session.user)
    ).filter(
        Session.start_time >= datetime.now()
    ).all()

# Async operations
async def send_notification_email(user_email: str, session_data: dict):
    async with aiohttp.ClientSession() as session:
        # Non-blocking email sending
        pass
```

### Frontend Optimization
```typescript
// Component memoization
const MemoizedSlotCard = React.memo(({ slot, onSelect }) => {
  return <SlotCard slot={slot} onSelect={onSelect} />
})

// Efficient re-renders
const [slots, setSlots] = useState<TimeSlot[]>([])
const availableSlots = useMemo(() => 
  slots.filter(slot => slot.available), [slots]
)
```

---

## Deployment Preparation

### Environment Variables
```bash
# Create deployment environment
cat > .env.production << EOF
DATABASE_URL=postgresql://user:secure_pass@db:5432/capcut_db
BOT_SERVICE_URL=http://bot:5001
FRONTEND_URL=https://yourdomain.com
GMAIL_APP_PASSWORD=production_app_password
ENVIRONMENT=production
HEADLESS=true
EOF
```

### Build Process
```bash
# Backend build
cd backend
pip install -r requirements.txt
python -m pytest tests/

# Frontend build  
cd frontend
npm ci
npm run build
npm run test

# Bot service build
cd bot
pip install -r requirements.txt
playwright install chromium
```
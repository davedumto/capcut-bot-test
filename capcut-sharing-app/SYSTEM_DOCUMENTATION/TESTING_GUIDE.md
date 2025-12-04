# CapCut Account Sharing System - Testing Guide

## Testing Strategy Overview

The testing approach covers multiple layers: unit tests, integration tests, end-to-end tests, and manual testing procedures for the three-service architecture.

---

## Test Environment Setup

### Prerequisites
```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-mock httpx
npm install --save-dev @testing-library/react @testing-library/jest-dom jest

# Setup test database
psql postgres -c "CREATE DATABASE capcut_test_db OWNER \"user\";"
```

### Environment Configuration
```bash
# Test environment variables (.env.test)
DATABASE_URL=postgresql://user:password@localhost:5432/capcut_test_db
BOT_SERVICE_URL=http://localhost:5002  # Different port for testing
FRONTEND_URL=http://localhost:3001
ENVIRONMENT=test
HEADLESS=true
DEBUG=false
```

---

## Backend Testing (FastAPI)

### Unit Tests Structure
```
backend/tests/
├── conftest.py                 # Test configuration and fixtures
├── test_models/               
│   ├── test_database.py       # Database model tests
│   └── test_schemas.py        # Pydantic schema validation tests
├── test_api/
│   ├── test_slots.py          # Slot management endpoint tests  
│   ├── test_bookings.py       # Booking endpoint tests
│   └── test_sessions.py       # Session management tests
├── test_services/
│   ├── test_password_service.py
│   ├── test_email_service.py
│   └── test_bot_service.py
└── test_scheduler/
    └── test_jobs.py           # Background job tests
```

### Test Configuration (conftest.py)
```python
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.database import Base, get_db

# Test database setup
TEST_DATABASE_URL = "postgresql://user:password@localhost:5432/capcut_test_db"
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

### API Endpoint Tests
```python
# tests/test_api/test_bookings.py
import pytest
from datetime import datetime, timedelta

def test_create_booking_success(client, db_session):
    """Test successful booking creation."""
    # Create test slot time
    slot_time = datetime.now() + timedelta(hours=2)
    slot_id = f"slot_{slot_time.strftime('%Y%m%d_%H%M')}"
    
    booking_data = {
        "name": "Test User",
        "email": "test@example.com",
        "slot_id": slot_id
    }
    
    response = client.post("/api/bookings", json=booking_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "sess_" in data["session_id"]
    assert "confirmed" in data["message"].lower()

def test_create_booking_invalid_slot(client):
    """Test booking with invalid slot ID."""
    booking_data = {
        "name": "Test User", 
        "email": "test@example.com",
        "slot_id": "invalid_slot_id"
    }
    
    response = client.post("/api/bookings", json=booking_data)
    assert response.status_code == 422  # Validation error

def test_create_booking_duplicate_slot(client, db_session):
    """Test booking same slot twice."""
    from app.models.database import Session as SessionModel, User
    
    # Create existing booking
    user = User(name="Existing User", email="existing@example.com")
    db_session.add(user)
    db_session.commit()
    
    slot_time = datetime.now() + timedelta(hours=2)
    existing_session = SessionModel(
        user_id=user.id,
        user_name=user.name,
        user_email=user.email,
        start_time=slot_time,
        end_time=slot_time + timedelta(minutes=90)
    )
    db_session.add(existing_session)
    db_session.commit()
    
    # Try to book same slot
    slot_id = f"slot_{slot_time.strftime('%Y%m%d_%H%M')}"
    booking_data = {
        "name": "New User",
        "email": "new@example.com", 
        "slot_id": slot_id
    }
    
    response = client.post("/api/bookings", json=booking_data)
    assert response.status_code == 400
    assert "no longer available" in response.json()["detail"]
```

### Service Layer Tests
```python
# tests/test_services/test_password_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.password_service import PasswordService

@pytest.fixture
def password_service():
    return PasswordService()

def test_generate_strong_password(password_service):
    """Test password generation meets requirements."""
    password = password_service.generate_password()
    
    assert len(password) >= 12
    assert any(c.islower() for c in password)  # Lowercase
    assert any(c.isupper() for c in password)  # Uppercase  
    assert any(c.isdigit() for c in password)  # Numbers
    assert any(c in "!@#$%^&*" for c in password)  # Special chars

@patch('app.services.password_service.bcrypt')
def test_hash_password(mock_bcrypt, password_service):
    """Test password hashing."""
    mock_bcrypt.hashpw.return_value = b'hashed_password'
    mock_bcrypt.gensalt.return_value = b'salt'
    
    result = password_service.hash_password("test_password")
    
    mock_bcrypt.gensalt.assert_called_once_with(rounds=12)
    mock_bcrypt.hashpw.assert_called_once()
    assert result == "hashed_password"

async def test_cleanup_expired_passwords(password_service, db_session):
    """Test automatic password cleanup."""
    from app.models.database import Password
    from datetime import datetime, timedelta
    
    # Create expired password
    expired_password = Password(
        password_hash="hash",
        plain_password="expired",
        expires_at=datetime.now() - timedelta(hours=2)
    )
    db_session.add(expired_password)
    db_session.commit()
    
    # Run cleanup
    await password_service.cleanup_expired_passwords(db_session)
    
    # Check password was cleaned
    updated_password = db_session.query(Password).filter_by(id=expired_password.id).first()
    assert updated_password.plain_password is None
```

### Scheduler Tests
```python  
# tests/test_scheduler/test_jobs.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from app.scheduler.jobs import session_start_job, session_end_job

@pytest.mark.asyncio
@patch('app.scheduler.jobs.get_db')
@patch('app.scheduler.jobs.call_bot_service')
async def test_session_start_job(mock_bot_service, mock_get_db, db_session):
    """Test session start job processes pending sessions."""
    from app.models.database import Session as SessionModel, User
    
    # Setup test data
    user = User(name="Test User", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    
    # Create session that should start
    session = SessionModel(
        user_id=user.id,
        user_name=user.name,
        user_email=user.email,
        start_time=datetime.now() - timedelta(minutes=1),  # Should have started
        end_time=datetime.now() + timedelta(minutes=89),
        status="pending"
    )
    db_session.add(session)
    db_session.commit()
    
    # Mock dependencies
    mock_get_db.return_value.__next__ = Mock(return_value=db_session)
    mock_bot_service.return_value = {"success": True, "new_password": "test_pass123"}
    
    # Run job
    await session_start_job()
    
    # Verify session was updated
    db_session.refresh(session)
    assert session.status == "active"
    mock_bot_service.assert_called_once()

@pytest.mark.asyncio
async def test_session_end_job_marks_completed(db_session):
    """Test session end job marks sessions as completed."""
    from app.models.database import Session as SessionModel
    
    # Create session that should end
    session = SessionModel(
        user_name="Test User",
        user_email="test@example.com", 
        start_time=datetime.now() - timedelta(minutes=100),
        end_time=datetime.now() - timedelta(minutes=10),  # Should have ended
        status="active"
    )
    db_session.add(session)
    db_session.commit()
    
    # Run job
    with patch('app.scheduler.jobs.get_db') as mock_get_db:
        mock_get_db.return_value.__next__ = Mock(return_value=db_session)
        await session_end_job()
    
    # Verify session was updated
    db_session.refresh(session)
    assert session.status == "completed"
```

---

## Frontend Testing (Next.js)

### Test Setup
```javascript
// jest.config.js
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/components/(.*)$': '<rootDir>/components/$1',
    '^@/pages/(.*)$': '<rootDir>/pages/$1',
    '^@/lib/(.*)$': '<rootDir>/lib/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
}

module.exports = createJestConfig(customJestConfig)
```

### Component Tests
```typescript
// __tests__/components/BookingForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import BookingForm from '@/components/BookingForm'

describe('BookingForm', () => {
  test('renders form fields correctly', () => {
    const mockSubmit = jest.fn()
    render(<BookingForm onSubmit={mockSubmit} />)
    
    expect(screen.getByLabelText('Name')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByText('Show Available Slots')).toBeInTheDocument()
  })

  test('validates required fields', async () => {
    const mockSubmit = jest.fn()
    render(<BookingForm onSubmit={mockSubmit} />)
    
    const submitButton = screen.getByText('Show Available Slots')
    expect(submitButton).toBeDisabled()
    
    // Fill name only
    fireEvent.change(screen.getByLabelText('Name'), {
      target: { value: 'Test User' }
    })
    expect(submitButton).toBeDisabled()
    
    // Fill email as well
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@example.com' }
    })
    expect(submitButton).toBeEnabled()
  })

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
    
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        name: 'Test User',
        email: 'test@example.com'
      })
    })
  })

  test('shows loading state during submission', async () => {
    const mockSubmit = jest.fn().mockImplementation(() => new Promise(resolve => 
      setTimeout(resolve, 100)
    ))
    render(<BookingForm onSubmit={mockSubmit} />)
    
    fireEvent.change(screen.getByLabelText('Name'), {
      target: { value: 'Test User' }
    })
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@example.com' }
    })
    
    fireEvent.click(screen.getByText('Show Available Slots'))
    
    expect(screen.getByText('Processing...')).toBeInTheDocument()
  })
})
```

### API Client Tests
```typescript
// __tests__/lib/api.test.ts
import { apiClient } from '@/lib/api'

// Mock fetch globally
global.fetch = jest.fn()

describe('API Client', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear()
  })

  test('getSlots makes correct API call', async () => {
    const mockSlots = {
      slots: [
        {
          id: 'slot_20241123_1400',
          start_time: '2024-11-23T14:00:00',
          end_time: '2024-11-23T15:30:00',
          available: true
        }
      ]
    }

    ;(fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockSlots
    })

    const result = await apiClient.getSlots()

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/slots',
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    )
    expect(result).toEqual(mockSlots)
  })

  test('createBooking handles success response', async () => {
    const bookingRequest = {
      name: 'Test User',
      email: 'test@example.com',
      slot_id: 'slot_20241123_1400'
    }

    const mockResponse = {
      success: true,
      session_id: 'sess_123',
      message: 'Booking confirmed'
    }

    ;(fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    })

    const result = await apiClient.createBooking(bookingRequest)

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/bookings',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookingRequest)
      }
    )
    expect(result).toEqual(mockResponse)
  })

  test('handles API error responses', async () => {
    ;(fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: async () => ({ detail: 'Slot no longer available' })
    })

    await expect(apiClient.getSlots()).rejects.toThrow('Slot no longer available')
  })

  test('handles network errors', async () => {
    ;(fetch as jest.Mock).mockRejectedValueOnce(new TypeError('Failed to fetch'))

    await expect(apiClient.getSlots()).rejects.toThrow('Unable to connect to the booking system')
  })
})
```

---

## Bot Service Testing

### Playwright Automation Tests
```python
# tests/test_bot/test_capcut_automation.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from playwright.async_api import async_playwright

@pytest.mark.asyncio
@patch('bot.services.gmail_handler.get_capcut_reset_link')
async def test_password_reset_flow_success(mock_gmail):
    """Test successful password reset flow."""
    mock_gmail.return_value = "https://capcut.com/reset?token=test123"
    
    from bot.services.capcut_bot import reset_password_forgot_flow
    
    # Mock browser automation
    with patch('bot.services.capcut_bot.async_playwright') as mock_playwright:
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Configure page interactions
        mock_page.wait_for_selector.return_value = AsyncMock()
        mock_page.query_selector_all.return_value = [AsyncMock(), AsyncMock()]  # Two password fields
        
        result = await reset_password_forgot_flow("test@example.com", "NewPass123!")
        
        assert result["success"] == True
        assert "successfully" in result["message"]
        
        # Verify browser cleanup
        mock_browser.close.assert_called_once()

@pytest.mark.asyncio
async def test_gmail_handler_fetches_reset_email():
    """Test Gmail IMAP integration."""
    from bot.services.gmail_handler import GmailHandler
    
    # Mock IMAP operations
    with patch('bot.services.gmail_handler.imaplib.IMAP4_SSL') as mock_imap:
        mock_mail = Mock()
        mock_imap.return_value = mock_mail
        
        # Mock email search results
        mock_mail.search.return_value = ('OK', [b'1 2 3'])
        mock_mail.fetch.return_value = ('OK', [(None, b'test email content with https://capcut.com/reset?token=abc123')])
        
        handler = GmailHandler("test@gmail.com", "app_password")
        result = handler.fetch_reset_email(max_wait_time=5)
        
        assert result is not None
        assert "reset_link" in result
        assert "capcut.com" in result["reset_link"]

def test_password_generator_strength():
    """Test password generator creates strong passwords."""
    from bot.services.password_generator import generate_strong_password
    
    for _ in range(10):  # Test multiple generations
        password = generate_strong_password()
        
        assert len(password) >= 12
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password) 
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*" for c in password)
```

---

## Integration Tests

### Cross-Service Integration
```python
# tests/test_integration/test_booking_flow.py
import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.asyncio
async def test_complete_booking_flow():
    """Test complete booking flow across all services."""
    
    # 1. Get available slots
    async with AsyncClient(app=app, base_url="http://test") as client:
        slots_response = await client.get("/api/slots")
        assert slots_response.status_code == 200
        
        slots = slots_response.json()["slots"]
        available_slot = next(slot for slot in slots if slot["available"])
        
        # 2. Create booking
        booking_data = {
            "name": "Integration Test User",
            "email": "integration@test.com",
            "slot_id": available_slot["id"]
        }
        
        booking_response = await client.post("/api/bookings", json=booking_data)
        assert booking_response.status_code == 200
        
        booking_result = booking_response.json()
        session_id = booking_result["session_id"]
        
        # 3. Verify session created
        session_response = await client.get(f"/api/sessions/{session_id}")
        assert session_response.status_code == 200
        
        session_data = session_response.json()
        assert session_data["user_email"] == "integration@test.com"
        assert session_data["status"] == "pending"

@pytest.mark.asyncio
@patch('app.services.bot_service.call_bot_service')
async def test_session_start_integration(mock_bot_service):
    """Test session start triggers bot service integration."""
    mock_bot_service.return_value = {
        "success": True,
        "new_password": "GeneratedPass123!"
    }
    
    # Create session that should start
    from app.scheduler.jobs import session_start_job
    
    # Setup test session in database
    # ... (session setup code)
    
    # Run scheduler job
    await session_start_job()
    
    # Verify bot service was called
    mock_bot_service.assert_called_once()
    call_args = mock_bot_service.call_args
    assert "/bot/reset-password" in str(call_args)
```

---

## Performance Tests

### Load Testing
```python
# tests/test_performance/test_load.py
import asyncio
import time
from httpx import AsyncClient

async def test_concurrent_bookings():
    """Test system handles concurrent booking requests."""
    
    async def create_booking(session_num):
        async with AsyncClient(app=app, base_url="http://test") as client:
            booking_data = {
                "name": f"Load Test User {session_num}",
                "email": f"loadtest{session_num}@example.com", 
                "slot_id": f"slot_20241123_{1400 + session_num}"
            }
            
            start_time = time.time()
            response = await client.post("/api/bookings", json=booking_data)
            duration = time.time() - start_time
            
            return response.status_code, duration
    
    # Test 50 concurrent bookings
    tasks = [create_booking(i) for i in range(50)]
    results = await asyncio.gather(*tasks)
    
    # Analyze results
    success_count = sum(1 for status, _ in results if status == 200)
    avg_duration = sum(duration for _, duration in results) / len(results)
    
    assert success_count >= 45  # Allow some failures under load
    assert avg_duration < 2.0   # Average response under 2 seconds
```

---

## Manual Testing Procedures

### Pre-Deployment Checklist

#### Frontend Testing
- [ ] Form validation works correctly
- [ ] Slot selection displays available times
- [ ] Booking confirmation shows correct details
- [ ] Responsive design works on mobile/tablet
- [ ] Error messages are user-friendly
- [ ] Loading states provide feedback

#### Backend Testing  
- [ ] All API endpoints return correct status codes
- [ ] Database queries execute efficiently
- [ ] Scheduler jobs run on schedule
- [ ] Email notifications are sent
- [ ] Error handling works gracefully
- [ ] Logs provide useful debugging information

#### Bot Service Testing
- [ ] Browser automation completes without errors
- [ ] Password generation meets security requirements
- [ ] Email processing handles various formats
- [ ] Rate limiting prevents abuse
- [ ] Headless mode works in production
- [ ] Error recovery handles timeouts

#### Integration Testing
- [ ] Cross-service communication works
- [ ] Data consistency across services
- [ ] Session lifecycle management
- [ ] Password rotation timing
- [ ] End-to-end booking flow
- [ ] Error propagation between services

### Testing with Real Credentials

#### Gmail Setup
```bash
# Test IMAP connection
python3 -c "
import imaplib
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('your_email@gmail.com', 'app_password')
mail.select('inbox')
status, messages = mail.search(None, 'ALL')
print(f'IMAP test successful: {len(messages[0].split())} emails found')
mail.logout()
"
```

#### CapCut Automation Test
```python
# Test browser automation without password reset
async def test_capcut_navigation():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to login page
        await page.goto("https://www.capcut.com/login")
        await page.wait_for_load_state("networkidle")
        
        # Check if page loaded correctly
        title = await page.title()
        assert "CapCut" in title
        
        await browser.close()
        print("✓ CapCut navigation test successful")
```

---

## Continuous Testing

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: capcut_test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install Python dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Install Node.js dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Install Playwright
      run: |
        cd bot
        pip install -r requirements.txt
        playwright install chromium
    
    - name: Run backend tests
      run: |
        cd backend
        pytest -v
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/capcut_test_db
    
    - name: Run frontend tests
      run: |
        cd frontend
        npm test
    
    - name: Run bot service tests
      run: |
        cd bot
        pytest -v
```
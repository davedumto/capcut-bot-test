# CapCut Account Sharing System - Architecture Documentation

## Technical Architecture Overview

### Service Communication Flow
```
User Request → Frontend → Backend → Bot Service → CapCut Website
     ↓             ↓          ↓           ↓
Booking Form → API Calls → Database → Browser Automation
     ↓             ↓          ↓           ↓  
Slot Selection → Schedule → Password → Email Reset
     ↓             ↓          ↓           ↓
Confirmation → Session → Storage → New Password
```

## Frontend Architecture (Next.js 15)

### Technology Stack
- **Framework:** Next.js 15 with App Router
- **Language:** TypeScript 5.6
- **Styling:** Tailwind CSS 3.4
- **State Management:** React useState hooks
- **API Communication:** Fetch API with custom client

### File Structure
```
frontend/
├── app/
│   ├── globals.css          # Global styles with custom color scheme
│   ├── layout.tsx           # Root layout with fonts and metadata
│   ├── page.tsx             # Main booking flow component
│   └── favicon.ico          # Application icon
├── components/
│   ├── BookingForm.tsx      # User details form
│   ├── ConfirmationModal.tsx # Booking confirmation UI
│   ├── Header.tsx           # Page header component
│   └── SlotSelector.tsx     # Time slot selection grid
├── lib/
│   ├── api.ts               # API client with type safety
│   └── utils.ts             # Time formatting utilities
├── package.json             # Dependencies and scripts
├── tailwind.config.js       # Custom color configuration
├── next.config.js           # Next.js configuration
└── tsconfig.json            # TypeScript configuration
```

### Custom Design System
```css
/* Color Palette */
--pale: #f5f2e8      /* Background */
--gold: #d4a574      /* Primary accent */
--rough: #4a3c28     /* Text headers */
--darknavy: #2c3e50  /* Body text */
--bookedslot: #e8e8e8 /* Disabled state */
```

### Component Architecture
1. **BookingForm.tsx**
   - Form validation with required fields
   - Loading states with spinner animation
   - Form submission handling

2. **SlotSelector.tsx** 
   - Real-time slot availability fetching
   - Time-based slot grouping (morning/afternoon/evening)
   - Booking confirmation modal
   - Past/available/booked slot styling

3. **ConfirmationModal.tsx**
   - Session details display
   - Password delivery information
   - Contact details for support

### State Management Pattern
```typescript
// Three-step wizard state
const [step, setStep] = useState<'form' | 'slots' | 'confirmation'>('form')
const [userDetails, setUserDetails] = useState<UserDetails | null>(null)
const [bookingData, setBookingData] = useState<BookingData | null>(null)

// API integration pattern
const handleBookingComplete = async (sessionId: string) => {
  const sessionData = await getSessionDetails(sessionId)
  setBookingData({ sessionId, startTime: sessionData.start_time, endTime: sessionData.end_time })
  setStep('confirmation')
}
```

## Backend Architecture (FastAPI)

### Technology Stack
- **Framework:** FastAPI with async/await
- **ORM:** SQLAlchemy 2.0+ with declarative base
- **Database:** PostgreSQL with psycopg2 driver
- **Scheduler:** APScheduler with AsyncIOScheduler
- **Email:** SMTP with Gmail integration
- **Configuration:** Pydantic Settings

### Service Layer Architecture
```
├── API Layer (FastAPI Routes)
│   ├── /api/slots - Time slot management
│   ├── /api/bookings - User booking operations
│   └── /api/sessions - Session status tracking
├── Business Logic Layer
│   ├── SessionService - Session lifecycle management  
│   ├── PasswordService - Password generation & cleanup
│   ├── EmailService - User notification system
│   └── BotService - Communication with bot service
├── Data Access Layer  
│   ├── SQLAlchemy Models - Database entity definitions
│   ├── Database Sessions - Connection management
│   └── Migration Scripts - Schema version control
└── Scheduler Layer
    ├── Session Start Jobs - Automated password generation
    ├── Session End Jobs - Password rotation
    └── Cleanup Jobs - Expired data removal
```

### Database Models
```python
# Core Entity Relationships
class User(Base):
    sessions = relationship("Session", back_populates="user")

class Session(Base):
    user = relationship("User", back_populates="sessions")
    passwords = relationship("Password", back_populates="session")

class Password(Base):
    session = relationship("Session", back_populates="passwords")
```

### Scheduler Architecture
```python
# Automated Job Management
session_start_job()   # Runs every minute - checks for starting sessions
session_end_job()     # Runs every minute - checks for ending sessions  
password_cleanup()    # Runs every 10 minutes - removes expired passwords
```

### API Endpoint Design
```python
# RESTful API with consistent response format
GET  /api/slots           → {"slots": [TimeSlot]}
POST /api/bookings        → {"success": bool, "session_id": str, "message": str}
GET  /api/sessions/active → ActiveSession | null
GET  /api/sessions/{id}   → SessionDetails
```

## Bot Service Architecture (FastAPI)

### Technology Stack  
- **Framework:** FastAPI for API endpoints
- **Automation:** Playwright for browser control
- **Email:** IMAP for Gmail integration
- **Security:** Stealth browsing techniques
- **Configuration:** Pydantic settings with .env

### Browser Automation Flow
```python
# 11-Step Password Reset Process
1. Clear browser cache/cookies
2. Navigate to CapCut login page  
3. Fill email field
4. Click Continue button
5. Click Forgot Password link
6. Confirm forgot password request
7. Fetch reset email via IMAP
8. Clear cache before reset link
9. Navigate to reset link
10. Fill new password fields  
11. Submit password reset form
```

### Stealth Techniques
```python
browser = await p.chromium.launch(
    args=[
        '--no-first-run',
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor'
    ]
)
context = await browser.new_context(
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    viewport={'width': 1920, 'height': 1080}
)
```

### Email Processing Architecture
```python
# Gmail IMAP Integration
class GmailHandler:
    - fetch_reset_email() - Search for CapCut emails
    - extract_email_content() - Parse email body
    - extract_reset_info() - Find reset links/codes
    - click_email_button_with_playwright() - Button automation
```

## Inter-Service Communication

### Backend ↔ Bot Service
```python
# HTTP API Communication
POST /bot/reset-password
{
    "email": "daevid621@gmail.com",
    "new_password": "generated_password" 
}
→ {"success": true, "new_password": "...", "message": "..."}
```

### Frontend ↔ Backend  
```typescript
// Type-Safe API Client
interface BookingRequest {
    name: string
    email: string
    slot_id: string
}
interface BookingResponse {
    success: boolean
    session_id: string
    message: string
}
```

## Security Architecture

### Password Security
- Bcrypt hashing for stored passwords
- Temporary plaintext storage (auto-deleted after 1 hour)
- Generated passwords: 12+ chars, mixed case, numbers, symbols

### Browser Security  
- Stealth user agents to avoid detection
- Cookie/cache clearing between sessions
- Headless mode for production deployment

### API Security
- CORS configuration for frontend-only access
- Input validation with Pydantic models
- No authentication (public booking system)

### Database Security
- Environment variable configuration
- Connection pooling with proper cleanup
- Foreign key constraints for data integrity

## Deployment Architecture

### Development Setup
```bash
# Three-service local development
Frontend:  npm run dev          (Port 3000)
Backend:   uvicorn app:app      (Port 8000)
Bot:       uvicorn app:app      (Port 5001)
Database:  PostgreSQL          (Port 5432)
```

### Docker Configuration
- Each service has individual Dockerfile
- Multi-stage builds for production optimization
- Environment variable injection
- Health check endpoints for monitoring

## Performance Considerations

### Frontend Optimization
- Static generation where possible
- Component-level loading states
- Efficient re-renders with proper state management
- Tailwind CSS purging for minimal bundle size

### Backend Optimization  
- Async/await throughout for I/O operations
- Database connection pooling
- Efficient SQL queries with proper indexing
- Background job processing with APScheduler

### Bot Service Optimization
- Browser instance reuse where possible
- Configurable timeouts for reliability
- Error handling with retry logic
- Memory cleanup after automation tasks

## Monitoring & Logging

### Application Logs
```python
# Structured logging across all services
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Session started", extra={"session_id": "sess_123"})
```

### Health Check Endpoints
```
GET /health        → {"status": "healthy"}
GET /scheduler/status → {"scheduler_running": true, "jobs": [...]}
```

### Database Monitoring
- Daily logs table for usage analytics
- Session status tracking
- Password expiration monitoring
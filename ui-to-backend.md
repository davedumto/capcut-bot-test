# Current UI to Backend System Flow

## What You Have Built

### Current Frontend UI
```
┌─────────────────────────────────────────────────┐
│  CapCut Pro Account Sharing                     │
│  Book your editing session (1.5 hours)          │
│  No account needed                              │
├─────────────────────────────────────────────────┤
│                                                 │
│  [User Details Box]                             │
│  ┌─────────────────────────────────────────────┐
│  │ david                          Edit Details │
│  │ david@gmail.com                             │
│  └─────────────────────────────────────────────┘
│                                                 │
│  AVAILABLE SLOTS                                │
│                                                 │
│  ☀️ Morning (6 AM - 12 PM)                     │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │ 6:00 AM  │ 7:30 AM  │ 9:00 AM  │ 10:30 AM │ │
│  │ to       │ to       │ to       │ to       │ │
│  │ 7:30 AM  │ 9:00 AM  │ 10:30 AM │ 12:00 PM │ │
│  │          │          │          │          │ │
│  │  Past    │  Past    │  Past    │  Past    │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
│                                                 │
│  🌤️ Afternoon (12 PM - 6 PM)                  │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │ 12:00 PM │ 1:30 PM  │ 3:00 PM  │ 4:30 PM  │ │
│  │ to       │ to       │ to       │ to       │ │
│  │ 1:30 PM  │ 3:00 PM  │ 4:30 PM  │ 6:00 PM  │ │
│  │          │          │          │          │ │
│  │  Past    │  Past    │  Past    │  Past    │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
│                                                 │
│  🌙 Evening (6 PM - 12 AM)                    │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │ 6:00 PM  │ 7:30 PM  │ 9:00 PM  │ 10:30 PM │ │
│  │ to       │ to       │ to       │ to       │ │
│  │ 7:30 PM  │ 9:00 PM  │ 10:30 PM │ 12:00 AM │ │
│  │          │          │          │          │ │
│  │  Past    │  Past    │   ✓      │   ✓      │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
│                                                 │
│  4 Available • Booked • 10 Past • 16 Total     │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Complete Flow: From UI to Backend to Bot

### Timeline

```
T+0: User is on the website
  ↓
T+1: User sees name/email already filled ("david", "david@gmail.com")
  ↓
T+2: User sees available slots:
     - Morning slots: "Past" (can't book)
     - Afternoon slots: "Past" (can't book)
     - Evening slots: "9:00 PM - 10:30 PM" ✓ Available
                      "10:30 PM - 12:00 AM" ✓ Available
  ↓
T+3: User clicks on "9:00 PM - 10:30 PM" slot (the Gold ✓ button)
  ↓
T+4: Frontend sends to Backend:
     POST /api/bookings
     {
       "name": "david",
       "email": "david@gmail.com",
       "slot_id": "9pm-1030pm"
     }
  ↓
T+5: Backend receives booking request:
     ✅ Validates: "david" hasn't booked today
     ✅ Validates: "david@gmail.com" hasn't booked today
     ✅ Validates: "9:00 PM - 10:30 PM" slot is available
     ✅ Creates session in database
        - session_id: "sess_12345"
        - user_name: "david"
        - user_email: "david@gmail.com"
        - start_time: "9:00 PM today"
        - end_time: "10:30 PM today"
        - status: "pending"
  ↓
T+6: Frontend receives response:
     {
       "success": true,
       "session_id": "sess_12345"
     }
  ↓
T+7: Frontend shows confirmation:
     "✅ Booking Confirmed!"
     "Your credentials will be sent to david@gmail.com"
     "Session starts in: X hours Y minutes"
  ↓
T+8 to T+(8 + hours until 9:00 PM): User waits
     - Checking email periodically
     - Waiting for credentials
  ↓
T+N (9:00 PM - Session Start Time Reached):
  ↓
  Backend Scheduler (runs every minute):
  ✅ Checks database for sessions where:
     - status == "pending"
     - start_time <= now
  ✅ Finds: session_12345 (9:00 PM slot)
  ✅ Calls Bot Service:
     POST http://localhost:5000/bot/reset-password
     {
       "email": "daevid621@gmail.com"
     }
  ↓
  Bot Service (runs in browser):
  ✅ Step 1: Navigate to CapCut login page
  ✅ Step 2: Enter email (daevid621@gmail.com)
  ✅ Step 3: Click Continue
  ✅ Step 4: Click Forgot Password
  ✅ Step 5: Confirm (sends reset email to daevid621@gmail.com)
  ✅ Step 6: Fetch reset link from Gmail via IMAP
  ✅ Step 7: Clear browser cache/cookies
  ✅ Step 8: Navigate to reset link
  ✅ Step 9: Fill new password fields
  ✅ Step 10: Click Confirm password
  ✅ Step 11: Return success
  ↓
  Bot returns to Backend:
  {
    "success": true,
    "new_password": "Tr0pic@lSun#23"
  }
  ↓
  Backend stores password:
  ✅ INSERT into passwords table:
     - password_hash: (bcrypt hashed)
     - plain_password: "Tr0pic@lSun#23" (expires in 1 hour)
     - session_id: "sess_12345"
  ✅ UPDATE session:
     - status: "active"
     - current_password_id: (from passwords table)
  ✓ Sends Email to david@gmail.com:
    ```
    Subject: CapCut Account Access Confirmed
    
    Hi david,
    
    Your booking is confirmed!
    
    📅 Date & Time:
    Start: 9:00 PM
    End: 10:30 PM
    
    ⏰ Important: Your session is STRICTLY TIME-LIMITED
    You will be automatically logged out at 10:30 PM
    
    🔐 Your CapCut Credentials:
    Email: daevid621@gmail.com
    Password: Tr0pic@lSun#23
    
    📝 Instructions:
    1. Go to https://www.capcut.com/login
    2. Use the credentials above
    3. Complete your edits before 10:30 PM
    4. Logout before your time expires
    
    ⚠️ Warning: Do NOT share these credentials
    ```
  ↓
T+N+1 minute: david receives email with credentials
  ↓
  David logs into CapCut:
  ✅ Goes to https://www.capcut.com/login
  ✅ Enters: daevid621@gmail.com
  ✅ Enters password: Tr0pic@lSun#23
  ✅ Starts editing
  ↓
T+N+90 minutes (10:30 PM - Session End Time):
  ↓
  Backend Scheduler (runs every minute):
  ✅ Checks database for sessions where:
     - status == "active"
     - end_time <= now
  ✅ Finds: session_12345 (9:00 PM - 10:30 PM slot, now ended)
  ✅ Calls Bot Service:
     POST http://localhost:5000/bot/reset-password
     (Same endpoint, bot generates NEW password)
  ↓
  Bot Service:
  ✅ Runs the 11-step forgot password flow again
  ✅ Generates NEW password: "Blu3Ocean$99"
  ↓
  Bot returns to Backend:
  {
    "success": true,
    "new_password": "Blu3Ocean$99"
  }
  ↓
  Backend stores NEW password:
  ✅ INSERT into passwords table:
     - password_hash: (bcrypt hashed)
     - plain_password: "Blu3Ocean$99"
     - session_id: "sess_12345"
  ✅ UPDATE session:
     - status: "completed"
  ✅ Check if another session is booked next:
     SELECT * FROM sessions
     WHERE start_time > 10:30 PM
     AND status = "pending"
     ORDER BY start_time ASC
     LIMIT 1
  ✅ Found: No next session (in this example)
  ↓
  If there WAS a next session:
  ✅ Send email to next user with NEW password
     "Hi [next_user],
      
      Your CapCut session is next!
      
      🔐 Credentials:
      Email: daevid621@gmail.com
      Password: Blu3Ocean$99
      
      Session starts in: X minutes"
  ↓
T+N+90+ minutes: david is auto-logged out (password changed)
  - When he tries to edit again, he gets "Invalid password" error
  - This prevents him from using the account beyond his 1.5 hours
  - Ensures the next user can log in with the new password
```

---

## Key Components Working Together

### 1. Frontend (What User Sees)
✅ **Current State:**
- Shows user details (name, email)
- Shows available slots grouped by time period
- Slots marked as "Past" (can't book) or "✓" Available
- User clicks on available slot
- Booking confirmed

✅ **What Happens:**
- Fetches slots from backend
- Sends booking request to backend
- Shows confirmation

### 2. Backend (The Brain)
✅ **What it Does:**
- Validates bookings
- Saves to PostgreSQL database
- Runs scheduler every minute
- Calls bot service when needed
- Sends emails to users
- Tracks session status

✅ **Database Tables:**
- `users` - User info (name, email)
- `sessions` - Booking info (time, user, status)
- `passwords` - Generated passwords (plain + hashed)

✅ **API Endpoints:**
- `GET /api/slots` - Returns available slots
- `POST /api/bookings` - Creates booking
- `GET /api/sessions/active` - Gets current session

### 3. Bot Service (The Executor)
✅ **What it Does:**
- Automates CapCut password reset
- Follows 11-step forgot password flow
- Extracts reset link from Gmail
- Fills password fields
- Returns new password

✅ **Called By:**
- Backend scheduler (when session starts or ends)

### 4. Scheduler (The Timer)
✅ **What it Does:**
- Runs every minute (APScheduler in backend)
- Checks for sessions that should START
- Checks for sessions that should END
- Calls bot to reset password
- Sends emails

---

## What Each Part Does

### When User Clicks on a Slot (9:00 PM - 10:30 PM)

**Frontend:**
```
User clicks ✓ button on "9:00 PM - 10:30 PM"
  ↓
Frontend calls: POST /api/bookings
{
  "name": "david",
  "email": "david@gmail.com",
  "slot_id": "9pm-1030pm"
}
```

**Backend:**
```
Receives POST /api/bookings
  ↓
Validates:
  ✅ Name "david" hasn't booked today (check database)
  ✅ Email "david@gmail.com" hasn't booked today (check database)
  ✅ Slot "9pm-1030pm" is available (check database)
  ↓
If all valid:
  ✅ Create session in database:
     INSERT INTO sessions (
       user_name="david",
       user_email="david@gmail.com",
       start_time="9:00 PM today",
       end_time="10:30 PM today",
       status="pending"
     )
  ✅ Return: {"success": true, "session_id": "sess_12345"}
  ↓
If invalid (e.g., already booked):
  ❌ Return: {"success": false, "message": "Already booked today"}
```

**Frontend:**
```
Receives response
  ↓
If success:
  ✅ Show confirmation modal
  ✅ Show countdown timer
  ✅ Show message: "Credentials will be sent to david@gmail.com"
  ↓
If error:
  ❌ Show error message
  ❌ Keep form visible for retry
```

---

### When 9:00 PM Arrives (Session Start Time)

**Backend Scheduler (runs every minute):**
```
Check database:
  SELECT * FROM sessions
  WHERE status = "pending"
  AND start_time <= NOW()
  ↓
Found: session_12345 (9:00 PM has arrived)
  ↓
Call Bot Service:
  POST http://localhost:5000/bot/reset-password
  {
    "email": "daevid621@gmail.com"
  }
```

**Bot Service:**
```
Receives request
  ↓
Generates strong password: "Tr0pic@lSun#23"
  ↓
Runs 11-step forgot password flow:
  1. Navigate to CapCut login
  2. Enter email: daevid621@gmail.com
  3. Click Continue
  4. Click Forgot Password
  5. Confirm (email sent)
  6. Fetch reset link from Gmail IMAP
  7. Clear browser cache
  8. Navigate to reset link
  9. Fill password: "Tr0pic@lSun#23" (twice)
  10. Click Confirm Password
  11. Verify success
  ↓
Return to Backend:
  {
    "success": true,
    "new_password": "Tr0pic@lSun#23"
  }
```

**Backend:**
```
Receives password from bot
  ↓
Store in database:
  INSERT INTO passwords (
    password_hash=bcrypt("Tr0pic@lSun#23"),
    plain_password="Tr0pic@lSun#23",
    session_id="sess_12345"
  )
  ↓
Update session:
  UPDATE sessions
  SET status="active"
  WHERE id="sess_12345"
  ↓
Send email to david@gmail.com:
  Subject: CapCut Account Access Confirmed
  
  Body:
    Email: daevid621@gmail.com
    Password: Tr0pic@lSun#23
    
    Session: 9:00 PM - 10:30 PM
    ⏰ WARNING: You will be auto-logged out at 10:30 PM
    
    Login at: https://www.capcut.com/login
```

**User (david) receives email:**
```
Clicks link or goes to CapCut
  ↓
Logs in with:
  Email: daevid621@gmail.com
  Password: Tr0pic@lSun#23
  ↓
Starts editing
  ↓
Edits for up to 1.5 hours
```

---

### When 10:30 PM Arrives (Session End Time)

**Backend Scheduler (runs every minute):**
```
Check database:
  SELECT * FROM sessions
  WHERE status = "active"
  AND end_time <= NOW()
  ↓
Found: session_12345 (10:30 PM has arrived)
  ↓
Call Bot Service:
  POST http://localhost:5000/bot/reset-password
  {
    "email": "daevid621@gmail.com"
  }
```

**Bot Service:**
```
Generates NEW password: "Blu3Ocean$99"
  ↓
Runs 11-step forgot password flow
  (Same as before, with new password)
  ↓
Returns:
  {
    "success": true,
    "new_password": "Blu3Ocean$99"
  }
```

**Backend:**
```
Store NEW password:
  INSERT INTO passwords (
    password_hash=bcrypt("Blu3Ocean$99"),
    plain_password="Blu3Ocean$99",
    session_id="sess_12345"
  )
  ↓
Update session:
  UPDATE sessions
  SET status="completed"
  WHERE id="sess_12345"
  ↓
Check for next user:
  SELECT * FROM sessions
  WHERE start_time > 10:30 PM
  AND status = "pending"
  ORDER BY start_time ASC
  LIMIT 1
  ↓
If next session exists:
  Send email to next user with new password
  ↓
If no next session:
  Password stays in database for future use
```

**Result:**
```
Old password (Tr0pic@lSun#23) is now INVALID
New password (Blu3Ocean$99) is now ACTIVE
  ↓
If david tries to continue editing:
  ❌ His old password doesn't work
  ❌ He's automatically logged out
  ↓
If next user wants to book:
  ✅ They already have the new password
  ✅ They can log in immediately
```

---

## Summary: What You Have Now

✅ **Frontend:** Beautiful UI that shows slots and booking interface
✅ **Backend API:** Accepts bookings, validates, stores in database
✅ **Scheduler:** Runs every minute, triggers bot at right times
✅ **Bot Service:** Automates CapCut password resets
✅ **Email Service:** Sends credentials to users at session start
✅ **Auto-Logout:** Password rotation ensures users can't access beyond their time

**The Complete System:**
1. User books a slot ✅
2. Backend saves booking ✅
3. At session start: Bot resets password ✅
4. User gets emailed credentials ✅
5. User can edit for 1.5 hours ✅
6. At session end: Bot changes password ✅
7. Old password invalid, user auto-logged out ✅
8. Next user gets new credentials ✅

**Everything is connected and automated!** 🎯
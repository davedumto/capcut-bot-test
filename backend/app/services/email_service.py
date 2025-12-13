"""
Email service for sending credentials and notifications
As specified in instructions.md
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465  # SSL port
        self.email = settings.gmail_user
        self.password = settings.gmail_app_password

    def _create_credentials_email(
        self, 
        user_name: str, 
        user_email: str,
        password: str,
        start_time: str,
        end_time: str
    ) -> MIMEMultipart:
        """Create email with CapCut credentials using template from instructions.md"""
        
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = user_email
        msg['Subject'] = "CapCut Account Access Confirmed"
        
        # Format start and end times
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        start_formatted = start_dt.strftime("%A, %B %d, %Y at %I:%M %p")
        end_formatted = end_dt.strftime("%A, %B %d, %Y at %I:%M %p")
        start_time_only = start_dt.strftime("%I:%M %p")
        end_time_only = end_dt.strftime("%I:%M %p")
        
        # Email body using exact template from instructions.md
        body = f"""Hi {user_name},

Your booking is confirmed!

📅 Date & Time:
Start: {start_formatted}
End: {end_formatted}

⏰ Important: Your session is STRICTLY TIME-LIMITED
You will be automatically logged out at {end_time_only}

🔐 Your CapCut Credentials:
Email: davidejere2001@gmail.com
Password: {password}

📝 Instructions:
1. Go to https://www.capcut.com/login
2. Use the credentials above
3. Complete your edits before {end_time_only}
4. Logout before your time expires to avoid interruption

⚠️ Warning: Do NOT share these credentials or attempt to extend your session.

Questions? Contact support@capcut-sharing.com"""

        msg.attach(MIMEText(body, 'plain'))
        return msg

    def send_credentials_email(
        self,
        user_name: str,
        user_email: str, 
        password: str,
        start_time: str,
        end_time: str
    ) -> bool:
        """Send credentials email to user"""
        try:
            msg = self._create_credentials_email(
                user_name, user_email, password, start_time, end_time
            )
            
            # Connect to server and send email using SSL
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Credentials email sent successfully to {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send credentials email to {user_email}: {e}")
            return False

    def send_booking_confirmation(
        self,
        user_name: str,
        user_email: str,
        start_time: str, 
        end_time: str
    ) -> bool:
        """Send booking confirmation email (optional feature)"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = user_email
            msg['Subject'] = "CapCut Booking Confirmed"
            
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            start_formatted = start_dt.strftime("%A, %B %d, %Y at %I:%M %p")
            end_formatted = end_dt.strftime("%A, %B %d, %Y at %I:%M %p")
            
            body = f"""Hi {user_name},

Your CapCut session has been booked successfully!

📅 Your Session:
Start: {start_formatted}
End: {end_formatted}
Duration: 1.5 hours

📧 You will receive your CapCut login credentials via email at session start time.

⏰ Important Reminders:
- Your session will start automatically at the scheduled time
- You will be logged out automatically when your session ends
- Please logout before your time expires to avoid interruption

Questions? Contact support@capcut-sharing.com

Thank you for using CapCut Sharing!"""

            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Booking confirmation sent to {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send booking confirmation to {user_email}: {e}")
            return False

    def send_magic_link(self, user_email: str, magic_link: str) -> bool:
        """
        Send magic link email for passwordless authentication
        Module 1: Authentication
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = user_email
            msg['Subject'] = "Sign in to CapCut Sharing"
            
            body = f"""Hi there!

Click the link below to sign in to your CapCut Sharing account:

{magic_link}

🔒 This link expires in 15 minutes for your security.
🚫 If you didn't request this, please ignore this email.

Questions? Contact support@capcut-sharing.com

CapCut Sharing Team"""

            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Magic link sent to {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send magic link to {user_email}: {e}")
            return False
    
    def send_manager_invite(self, manager_email: str, manager_name: str, temp_password: str) -> bool:
        """
        Send manager invitation email with temporary password
        Module 1: Authentication & Module 9: Admin Panel
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = manager_email
            msg['Subject'] = "Welcome to CapCut Sharing - Manager Account"
            
            login_url = f"{self._get_frontend_url()}/auth/login"
            
            body = f"""Hi {manager_name},

Welcome to CapCut Sharing! You've been invited to manage a team.

🔑 Your login credentials:
Email: {manager_email}
Temporary Password: {temp_password}

👉 Sign in here: {login_url}

⚠️ You'll be required to change your password on first login.

Next steps:
1. Sign in and change your password
2. Add your CapCut Pro credentials
3. Add your team members (up to 12)

Questions? Contact support@capcut-sharing.com

CapCut Sharing Team"""

            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Manager invite sent to {manager_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send manager invite to {manager_email}: {e}")
            return False
    
    def send_password_reset(self, user_email: str, reset_link: str) -> bool:
        """
        Send password reset email to manager
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = user_email
            msg['Subject'] = "Reset Your Password - Slotio"
            
            body = f"""Hi there,

You requested to reset your password on Slotio.

Click the link below to reset your password:

{reset_link}

🔒 This link expires in 1 hour for your security.
🚫 If you didn't request this, please ignore this email.

After clicking, you'll be logged in and prompted to set a new password.

Questions? Contact support@capcut-sharing.com

Slotio Team"""

            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Password reset email sent to {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset to {user_email}: {e}")
            return False
    
    def _get_frontend_url(self) -> str:
        """Get frontend URL from config"""
        return settings.frontend_url


# Singleton instance
email_service = EmailService()
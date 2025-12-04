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
Email: thehimspiredshop@gmail.com
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


# Singleton instance
email_service = EmailService()
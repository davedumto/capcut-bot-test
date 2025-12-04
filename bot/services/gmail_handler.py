#!/usr/bin/env python3
"""
Gmail IMAP Handler for CapCut reset emails
Extracted from existing test_capcut.py
"""

import time
import imaplib
import email
import re
import logging
from datetime import datetime
from email.header import decode_header

logger = logging.getLogger(__name__)


class GmailHandler:
    """Handle Gmail IMAP operations for fetching reset emails"""
    
    def __init__(self, email_address: str, app_password: str):
        self.email_address = email_address
        self.app_password = app_password
        self.imap_host = "imap.gmail.com"
    
    def log_with_timestamp(self, message: str):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{timestamp}] {message}")
    
    def fetch_reset_email(self, max_wait_time: int = 60) -> dict:
        """
        Fetch the latest CapCut reset email from Gmail using IMAP
        
        Returns:
            dict: {
                "reset_link": "https://...",
                "verification_code": "123456" (if applicable),
                "subject": "Email subject"
            }
        """
        self.log_with_timestamp("Connecting to Gmail via IMAP...")
        
        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL(self.imap_host)
            mail.login(self.email_address, self.app_password)
            mail.select("inbox")
            
            self.log_with_timestamp("Searching for CapCut emails...")
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                # Search for emails from CapCut (try different search approaches)
                search_terms = [
                    'FROM admin@mail.capcut.com',
                    'FROM capcut',
                    'FROM tiktok', 
                    'FROM bytedance',
                    'SUBJECT reset',
                    'SUBJECT password',
                    'SUBJECT verification'
                ]
                
                status, messages = None, None
                for term in search_terms:
                    try:
                        status, messages = mail.search(None, term)
                        if status == "OK" and messages[0]:
                            self.log_with_timestamp(f"Found emails using search term: {term}")
                            break
                    except Exception as e:
                        self.log_with_timestamp(f"Search term '{term}' failed: {e}")
                        continue
                
                # Fallback: get all recent emails if specific searches failed
                if not (status == "OK" and messages[0]):
                    try:
                        status, messages = mail.search(None, 'ALL')
                        if status == "OK" and messages[0]:
                            self.log_with_timestamp("Using fallback: checking all recent emails")
                    except Exception as e:
                        self.log_with_timestamp(f"Fallback search failed: {e}")
                        continue
                
                if status == "OK" and messages[0]:
                    email_ids = messages[0].split()
                    
                    # Check the latest emails first (last 10 emails)
                    for email_id in reversed(email_ids[-10:]):
                        try:
                            status, msg_data = mail.fetch(email_id, "(RFC822)")
                            
                            if status == "OK":
                                email_body = msg_data[0][1]
                                email_message = email.message_from_bytes(email_body)
                                
                                # Get email subject
                                subject = email_message["Subject"]
                                if subject:
                                    subject = decode_header(subject)[0][0]
                                    if isinstance(subject, bytes):
                                        subject = subject.decode()
                                
                                self.log_with_timestamp(f"Checking email subject: {subject}")
                                
                                # Check if this is a reset/verification email
                                reset_keywords = ['reset', 'code', 'verify', 'verification', 'password', 'confirm']
                                if any(keyword.lower() in str(subject).lower() for keyword in reset_keywords):
                                    self.log_with_timestamp(f"Found CapCut reset email: {subject}")
                                    
                                    # Extract email content
                                    email_content = self._extract_email_content(email_message)
                                    
                                    if email_content:
                                        # Parse reset information
                                        reset_info = self._extract_reset_info(email_content)
                                        if reset_info:
                                            reset_info['subject'] = subject
                                            mail.logout()
                                            return reset_info
                        
                        except Exception as e:
                            self.log_with_timestamp(f"Error processing email {email_id}: {e}")
                            continue
                
                self.log_with_timestamp("Waiting for reset email... (checking again in 5 seconds)")
                time.sleep(5)
            
            mail.logout()
            self.log_with_timestamp("Timeout waiting for reset email")
            return None
            
        except Exception as e:
            self.log_with_timestamp(f"Error accessing Gmail: {e}")
            return None
    
    def _extract_email_content(self, email_message) -> str:
        """Extract text content from email message"""
        try:
            email_content = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        email_content = part.get_payload(decode=True).decode()
                        break
                    elif part.get_content_type() == "text/html":
                        email_content = part.get_payload(decode=True).decode()
            else:
                email_content = email_message.get_payload(decode=True).decode()
            
            return email_content
            
        except Exception as e:
            self.log_with_timestamp(f"Error extracting email content: {e}")
            return ""
    
    def _extract_reset_info(self, email_content: str) -> dict:
        """
        Extract reset code, link, and button info from email content
        
        Returns:
            dict: {
                "reset_link": "https://..." (if found),
                "verification_code": "123456" (if found),
                "has_button": True/False,
                "button_text": "Reset Password" (if found),
                "email_html": "full html content" (for button clicking)
            }
        """
        self.log_with_timestamp("Parsing email for reset code/link/button...")
        
        result = {}
        result['email_html'] = email_content  # Store full HTML for button clicking
        
        # Look for button elements first (prioritize buttons over manual links)
        button_patterns = [
            # CapCut specific button patterns (most specific first)
            r'<a[^>]*href=[\'"]([^\'"]*forget-password[^\'"]*)[\'"][^>]*>([^<]*(?:Reset|reset)[^<]*)</a>',
            r'<a[^>]*href=[\'"]([^\'"]*capcut\.com[^\'"]*)[\'"][^>]*>([^<]*(?:Reset|reset|password)[^<]*)</a>',
            
            # General button patterns
            r'<a[^>]*(?:button|btn)[^>]*href=[\'"]([^\'"]*)[\'"][^>]*>([^<]*(?:reset|password|confirm)[^<]*)</a>',
            r'<a[^>]*href=[\'"]([^\'"]*(?:reset|password|token)[^\'"]*)[\'"][^>]*>([^<]*(?:reset|password|confirm)[^<]*)</a>',
            r'<button[^>]*>([^<]*(?:reset|password|confirm)[^<]*)</button>',
            r'<a[^>]*(?:button|btn)[^>]*>([^<]*(?:reset|password|confirm)[^<]*)</a>',
            r'<td[^>]*(?:button|btn)[^>]*>.*?<a[^>]*href=[\'"]([^\'"]*)[\'"][^>]*>([^<]*(?:reset|password|confirm)[^<]*)</a>',
        ]
        
        for pattern in button_patterns:
            matches = re.findall(pattern, email_content, re.IGNORECASE | re.DOTALL)
            if matches:
                self.log_with_timestamp(f"Found button pattern: {pattern[:60]}...")
                result['has_button'] = True
                
                # Handle different match formats
                for match in matches:
                    if isinstance(match, tuple):
                        # For patterns that capture both URL and text
                        if len(match) == 2:
                            url, text = match
                            if 'http' in url:
                                # Decode HTML entities in URL
                                import html
                                decoded_url = html.unescape(url.strip())
                                result['reset_link'] = decoded_url
                                result['button_text'] = text.strip()
                                self.log_with_timestamp(f"Found reset button: '{text.strip()}' -> {decoded_url}")
                                break
                    else:
                        # For patterns that only capture text
                        result['button_text'] = match.strip()
                        self.log_with_timestamp(f"Found reset button: {match.strip()}")
                
                if 'reset_link' in result:
                    break
        
        if not result.get('has_button'):
            # Fallback: Look for reset links manually
            link_patterns = [
                r'https://[^\s<>"\']+(?:reset|password|token)[^\s<>"\']*',
                r'https://[^\s<>"\']*capcut\.com[^\s<>"\']*(?:reset|password|token)[^\s<>"\']*',
                r'https://[^\s<>"\']*capcut\.com[^\s<>"\']*',
                r'https://[^\s<>"\']+password[^\s<>"\']*',
                r'https://[^\s<>"\']+verify[^\s<>"\']*',
                r'https://[^\s<>"\']+token[^\s<>"\']*'
            ]
            
            for pattern in link_patterns:
                matches = re.findall(pattern, email_content, re.IGNORECASE)
                for link in matches:
                    # Clean up the link (remove trailing punctuation)
                    link = re.sub(r'[.,;!?]+$', '', link)
                    if 'capcut.com' in link.lower() or any(keyword in link.lower() for keyword in ['reset', 'password', 'token']):
                        # Decode HTML entities in URL
                        import html
                        decoded_link = html.unescape(link)
                        self.log_with_timestamp(f"Found reset link: {decoded_link}")
                        result['reset_link'] = decoded_link
                        break
                
                if 'reset_link' in result:
                    break
        
        # Look for verification codes
        code_patterns = [
            r'\b\d{6}\b',  # 6-digit code
            r'\b\d{4}\b',  # 4-digit code
            r'code[:\s]+(\d+)',  # "code: 123456"
            r'verification[:\s]+(\d+)',  # "verification: 123456"
        ]
        
        for pattern in code_patterns:
            match = re.search(pattern, email_content, re.IGNORECASE)
            if match:
                code = match.group(1) if match.groups() else match.group(0)
                self.log_with_timestamp(f"Found reset code: {code}")
                result['verification_code'] = code
                break
        
        if not result.get('has_button') and not result.get('reset_link'):
            self.log_with_timestamp("No reset button, code, or link found in email")
            return None
        
        return result
    
    def click_email_button_with_playwright(self, email_html: str, button_text: str = None):
        """
        Use Playwright to render the email HTML and click the reset button
        
        Returns:
            str: The URL that the button click navigated to, or None if failed
        """
        try:
            from playwright.sync_api import sync_playwright
            
            self.log_with_timestamp("Using Playwright to click email button...")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                try:
                    # Create a data URL with the email HTML
                    import base64
                    email_html_b64 = base64.b64encode(email_html.encode('utf-8')).decode('ascii')
                    data_url = f"data:text/html;base64,{email_html_b64}"
                    
                    page.goto(data_url)
                    
                    # Wait for page to load
                    page.wait_for_load_state("networkidle", timeout=5000)
                    
                    # Look for clickable button elements
                    button_selectors = [
                        'a[href*="reset"]',
                        'a[href*="password"]', 
                        'a[href*="capcut"]',
                        'button:has-text("reset")',
                        'button:has-text("password")',
                        'button:has-text("confirm")',
                        'a:has-text("reset")',
                        'a:has-text("password")',
                        'a:has-text("confirm")',
                    ]
                    
                    if button_text:
                        # Add specific button text selector
                        button_selectors.insert(0, f'a:has-text("{button_text}")')
                        button_selectors.insert(0, f'button:has-text("{button_text}")')
                    
                    clicked_url = None
                    for selector in button_selectors:
                        try:
                            element = page.wait_for_selector(selector, timeout=2000)
                            if element and element.is_visible():
                                self.log_with_timestamp(f"Found clickable button with selector: {selector}")
                                
                                # Get the href if it's a link
                                href = element.get_attribute('href')
                                if href and href.startswith('http'):
                                    clicked_url = href
                                    self.log_with_timestamp(f"Button click would navigate to: {href}")
                                    break
                                    
                        except:
                            continue
                    
                    return clicked_url
                    
                finally:
                    browser.close()
                    
        except Exception as e:
            self.log_with_timestamp(f"Error clicking email button: {e}")
            return None


# IMAP helper to fetch reset link from Gmail
# Extracted from the bot forgot password flow for reusability

def get_capcut_reset_link(email_address, app_password):
    """
    Fetch the password reset link from CapCut email
    
    Args:
        email_address: Gmail address
        app_password: Gmail app password (not regular password)
        
    Returns:
        str: Reset link URL or None
    """
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        imap.login(email_address, app_password)
        imap.select("INBOX")
        
        # Search for latest email from CapCut
        status, messages = imap.search(None, "FROM", "admin@mail.capcut.com")
        email_ids = messages[0].split()
        
        if not email_ids:
            logger.warning("No CapCut emails found")
            return None
        
        # Get the latest email
        latest_email_id = email_ids[-1]
        status, msg = imap.fetch(latest_email_id, "(RFC822)")
        msg = email.message_from_bytes(msg[0][1])
        
        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() in ["text/plain", "text/html"]:
                    body = part.get_payload(decode=True).decode()
        else:
            body = msg.get_payload(decode=True).decode()
        
        # Find reset link
        link_pattern = r'https://[^\s\)"<]+'
        matches = re.findall(link_pattern, body)
        
        for link in matches:
            if "capcut.com" in link and any(x in link for x in ["reset", "password", "token"]):
                imap.close()
                imap.logout()
                logger.info("Reset link found in email")
                return link
        
        imap.close()
        imap.logout()
        logger.warning("Could not extract reset link from email")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching email: {e}")
        return None
#!/usr/bin/env python3
"""
CapCut Bot Test Script
This script tests CapCut login and password reset functionality with Gmail integration.
"""

import time
import imaplib
import email
import re
import secrets
import string
from datetime import datetime
from email.header import decode_header
from playwright.sync_api import sync_playwright, TimeoutError


def generate_strong_password(length=16):
    """Generate a strong password using secrets module."""
    # Define character sets
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*"
    
    # Ensure at least one character from each set
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]
    
    # Fill the rest randomly from all character sets
    all_chars = uppercase + lowercase + digits + special
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle the password list to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def log_with_timestamp(message):
    """Print message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def handle_all_banners_and_modals(page, max_attempts=2):
    """Handle all types of banners, modals, and overlays that might appear."""
    log_with_timestamp("Checking for banners, modals, and overlays...")
    
    # PRIORITY 1: Handle cookie banners FIRST with longer timeout
    log_with_timestamp("Checking for cookie banner (priority)...")
    cookie_selectors = [
        'button:has-text("Accept")',
        'button:has-text("Accept all")', 
        'button:has-text("Allow all")',
        'tiktok-cookie-banner button',
        '.cookie-banner button',
        '#cookie-banner button',
        'button[id*="accept"]',
        'button[class*="accept"]'
    ]
    
    # Try cookie banner with longer timeout
    cookie_handled = False
    for selector in cookie_selectors:
        try:
            cookie_element = page.wait_for_selector(selector, timeout=5000)
            if cookie_element and cookie_element.is_visible():
                log_with_timestamp(f"Found cookie banner with selector: {selector}")
                cookie_element.click()
                time.sleep(2)  # Longer pause for cookie banner
                cookie_handled = True
                log_with_timestamp("Cookie banner accepted successfully")
                break
        except TimeoutError:
            continue
        except Exception as e:
            continue
    
    if not cookie_handled:
        log_with_timestamp("No cookie banner found")
    
    # PRIORITY 2: Handle other banners and modals (be more specific to avoid clicking login buttons)
    other_selectors = [
        # AI modal banners  
        '.ai-modal button:has-text("Got it")',
        '.ai-modal button:has-text("OK")',
        '.ai-modal button:has-text("Close")',
        '.ai-banner button',
        'button:has-text("Try AI Features")',
        '.ai-guide-mask button',
        # Specific modal overlays (avoid generic primary buttons)
        'button.lv-btn.lv-btn-primary.lv-btn-size-mini.lv-btn-shape-square.footer-btn-S2XvXp',
        'button:has-text("OK")',
        'button:has-text("Got it")',
        'button:has-text("Skip")',
        'button:has-text("Close")',
        '.lv-modal-wrapper button',
        '.modal-footer button',
        '.guide-mask button',
        '.workspace-ai-home-guide-mask button',
        # Tutorial/tooltip overlays
        'button:has-text("Next")',
        'button:has-text("Finish")',
        'button:has-text("Done")',
        '.tooltip button',
        '.tour-step button',
        '.tutorial-overlay button'
    ]
    
    # Try multiple rounds to catch any banners that appear dynamically
    for attempt in range(max_attempts):
        found_any = False
        log_with_timestamp(f"Other banner check round {attempt + 1}...")
        
        for selector in other_selectors:
            try:
                element = page.wait_for_selector(selector, timeout=1000)  # Shorter timeout
                if element and element.is_visible():
                    log_with_timestamp(f"Found banner/modal with selector: {selector}")
                    element.click()
                    time.sleep(0.5)  # Shorter pause
                    found_any = True
                    log_with_timestamp(f"Dismissed banner/modal: {selector}")
                    break  # Break after finding first modal to avoid clicking too many
            except TimeoutError:
                continue
            except Exception as e:
                # Continue even if one selector fails
                continue
        
        # If no banners found in this round, we're done
        if not found_any:
            log_with_timestamp("No more banners/modals found")
            break
        
        # Brief pause between rounds
        time.sleep(0.5)
    
    log_with_timestamp("Banner/modal handling completed")


def fetch_capcut_email(email_address, app_password, max_wait_time=60):
    """Fetch the latest CapCut reset email from Gmail using IMAP."""
    print("Connecting to Gmail via IMAP...")
    
    try:
        # Connect to Gmail IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_address, app_password)
        mail.select("inbox")
        
        print("Searching for CapCut emails...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            # Search for emails from CapCut (try different search approaches)
            search_terms = [
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
                        print(f"Found emails using search term: {term}")
                        break
                except:
                    continue
            
            # Fallback: get all recent emails if specific searches failed
            if not (status == "OK" and messages[0]):
                try:
                    status, messages = mail.search(None, 'ALL')
                    if status == "OK" and messages[0]:
                        print("Using fallback: checking all recent emails")
                except:
                    pass
            
            if status == "OK" and messages[0]:
                email_ids = messages[0].split()
                
                # Check the latest emails first
                for email_id in reversed(email_ids[-10:]):  # Check last 10 emails
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
                        
                        print(f"Checking email subject: {subject}")
                        
                        # Check if this is a reset/verification email
                        reset_keywords = ['reset', 'code', 'verify', 'verification', 'password', 'confirm']
                        if any(keyword.lower() in subject.lower() for keyword in reset_keywords):
                            print(f"Found CapCut reset email: {subject}")
                            
                            # Extract email content
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
                            
                            mail.logout()
                            return email_content, subject
            
            print("Waiting for reset email... (checking again in 5 seconds)")
            time.sleep(5)
        
        mail.logout()
        print("Timeout waiting for reset email")
        return None, None
        
    except Exception as e:
        print(f"Error accessing Gmail: {e}")
        return None, None


def extract_reset_info(email_content):
    """Extract reset code or link from email content."""
    log_with_timestamp("Parsing email for reset code/link...")
    
    # Look for reset links first (prioritize links over codes)
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
                log_with_timestamp(f"Found reset link: {link}")
                return {"type": "link", "value": link}
    
    # Look for verification codes as fallback
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
            log_with_timestamp(f"Found reset code: {code}")
            return {"type": "code", "value": code}
    
    log_with_timestamp("No reset code or link found in email")
    return None


def test_capcut_password_reset():
    """Test script that tests complete CapCut password reset flow with login verification."""
    
    # Generate strong password
    new_password = generate_strong_password(16)
    log_with_timestamp("=== GENERATED NEW PASSWORD ===")
    log_with_timestamp(f"New Password: {new_password}")
    log_with_timestamp("===============================")
    
    # Credentials
    EMAIL = "daevid621@gmail.com"
    CURRENT_PASSWORD = "Doomsday2022."
    GMAIL_APP_PASSWORD = "vrecwdtlranpytll"
    LOGIN_URL = "https://www.capcut.com/login?redirect_url=https%3A%2F%2Fwww.capcut.com%2Fmy-edit&from_page=landing_page&enter_from=a1.b1.c1.0"
    
    with sync_playwright() as p:
        # Launch browser in non-headless mode so you can see what's happening
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Step 1: Initial login with current password
            log_with_timestamp("=== STEP 1: LOGGING IN WITH CURRENT PASSWORD ===")
            page.goto(LOGIN_URL, timeout=30000)
            log_with_timestamp(f"Page loaded. Current URL: {page.url}")
            
            # Handle cookie banner IMMEDIATELY after page load
            time.sleep(2)  # Brief wait for page to render
            handle_all_banners_and_modals(page)
            
            # Now wait for network to be idle (shorter timeout)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
                log_with_timestamp("Page network idle achieved")
            except TimeoutError:
                log_with_timestamp("Network idle timeout - proceeding anyway")
            
            # Fill email with multiple selector strategies
            log_with_timestamp("Filling email for initial login...")
            email_selectors = [
                'input[placeholder="Enter email"]',
                'input[type="email"]',
                'input[name="email"]',
                'input[id*="email"]',
                'input[class*="email"]'
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = page.wait_for_selector(selector, timeout=5000)
                    if email_input and email_input.is_visible():
                        log_with_timestamp(f"Found email input with selector: {selector}")
                        break
                except TimeoutError:
                    continue
            
            if email_input:
                # Clear any existing content and fill email
                email_input.click()
                email_input.fill('')
                email_input.fill(EMAIL)
                log_with_timestamp(f"Email filled: {EMAIL}")
            else:
                log_with_timestamp("ERROR: Could not find email input field")
                raise Exception("Email input field not found")
            
            # Click continue
            continue_btn = page.wait_for_selector('button:has-text("Continue")', timeout=10000)
            continue_btn.click()
            time.sleep(3)
            
            # Fill current password
            log_with_timestamp("Filling current password...")
            password_input = page.wait_for_selector('input[placeholder="Enter password"]', timeout=10000)
            password_input.fill(CURRENT_PASSWORD)
            
            # Click login
            login_btn = page.wait_for_selector('button:has-text("Sign In")', timeout=10000)
            login_btn.click()
            
            # Wait for dashboard
            log_with_timestamp("Waiting for dashboard...")
            time.sleep(5)
            
            # Handle any tutorial/guide overlays
            try:
                overlay_selectors = ['.guide-mask', 'button:has-text("Got it")', 'button:has-text("Skip")']
                for selector in overlay_selectors:
                    try:
                        overlay = page.wait_for_selector(selector, timeout=3000)
                        if overlay:
                            overlay.click()
                            time.sleep(2)
                            break
                    except TimeoutError:
                        continue
            except:
                pass
            
            if "my-edit" in page.url or "dashboard" in page.url:
                log_with_timestamp("SUCCESS: Initial login successful")
            else:
                log_with_timestamp(f"WARNING: Login may have failed. Current URL: {page.url}")
            
            # Step 2: Logout
            log_with_timestamp("=== STEP 2: LOGGING OUT ===")
            
            # Handle any banners and modals that might block interaction
            handle_all_banners_and_modals(page)
            
            # Find and click avatar
            avatar_selectors = [
                'span.lv-avatar-image',
                'img[alt="avatar"]',
                '.avatar',
                '.user-avatar'
            ]
            
            avatar_element = None
            for selector in avatar_selectors:
                try:
                    avatar_element = page.wait_for_selector(selector, timeout=5000)
                    log_with_timestamp(f"Found avatar with selector: {selector}")
                    break
                except TimeoutError:
                    continue
            
            if not avatar_element:
                raise Exception("Could not find avatar for logout")
            
            log_with_timestamp("Clicking avatar...")
            avatar_element.click()
            time.sleep(2)
            
            # Find and click sign out
            signout_element = page.wait_for_selector('text="Sign out"', timeout=10000)
            log_with_timestamp("Clicking Sign out...")
            signout_element.click()
            time.sleep(3)
            
            log_with_timestamp("SUCCESS: Logged out successfully")
            
            # Step 3: Clear cache and cookies
            log_with_timestamp("=== STEP 3: CLEARING CACHE AND COOKIES ===")
            context.clear_cookies()
            log_with_timestamp("Cookies cleared")
            page.goto('about:blank')
            log_with_timestamp("Cache cleared - navigated to about:blank")
            
            # Step 4: Start forgot password flow
            log_with_timestamp("=== STEP 4: STARTING FORGOT PASSWORD FLOW ===")
            page.goto(LOGIN_URL, timeout=30000)
            log_with_timestamp("Page loaded for password reset")
            
            # Handle cookie banner IMMEDIATELY after page load
            time.sleep(2)  # Brief wait for page to render
            handle_all_banners_and_modals(page)
            
            # Now wait for network to be idle (shorter timeout)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
                log_with_timestamp("Page network idle achieved")
            except TimeoutError:
                log_with_timestamp("Network idle timeout - proceeding anyway")
            log_with_timestamp("Navigated to login page for password reset")
            
            # Fill email with multiple selector strategies
            log_with_timestamp("Filling email for password reset...")
            email_selectors = [
                'input[placeholder="Enter email"]',
                'input[type="email"]',
                'input[name="email"]',
                'input[id*="email"]',
                'input[class*="email"]'
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = page.wait_for_selector(selector, timeout=5000)
                    if email_input and email_input.is_visible():
                        log_with_timestamp(f"Found email input with selector: {selector}")
                        break
                except TimeoutError:
                    continue
            
            if email_input:
                # Clear any existing content and fill email
                email_input.click()
                email_input.fill('')
                email_input.fill(EMAIL)
                log_with_timestamp(f"Email filled: {EMAIL}")
            else:
                log_with_timestamp("ERROR: Could not find email input field")
                raise Exception("Email input field not found")
            
            # Click continue
            continue_btn = page.wait_for_selector('button:has-text("Continue")', timeout=10000)
            continue_btn.click()
            time.sleep(3)
            
            # Click forgot password
            log_with_timestamp("Looking for 'Forgot password?' button...")
            forgot_password_selectors = [
                'div.forget-pwd-btn',
                '.forget-pwd-btn',
                'button:has-text("Forgot password?")',
                'a:has-text("Forgot password?")',
                'text="Forgot password?"'
            ]
            
            forgot_btn = None
            for selector in forgot_password_selectors:
                try:
                    forgot_btn = page.wait_for_selector(selector, timeout=5000)
                    log_with_timestamp(f"Found 'Forgot password?' button with selector: {selector}")
                    break
                except TimeoutError:
                    continue
            
            if not forgot_btn:
                raise Exception("Could not find 'Forgot password?' button")
            
            log_with_timestamp("Clicking 'Forgot password?' button...")
            forgot_btn.click()
            time.sleep(3)
            
            # Find continue button to trigger email
            log_with_timestamp("Looking for continue button to trigger reset email...")
            continue_selectors = [
                'button.lv-btn.lv-btn-primary.lv-btn-size-default.lv-btn-shape-square.lv_forget_pwd_panel-btn.lv_forget_pwd_panel-btn-reset.lv_sign_in_panel_wide-primary-button',
                '.lv_forget_pwd_panel-btn-reset',
                '.lv_forget_pwd_panel-btn',
                'button:has-text("Continue")',
                'button:has-text("Send")',
                'button[type="submit"]',
                'button.lv-btn-primary'
            ]
            
            email_continue_btn = None
            for selector in continue_selectors:
                try:
                    email_continue_btn = page.wait_for_selector(selector, timeout=5000)
                    log_with_timestamp(f"Found continue button with selector: {selector}")
                    break
                except TimeoutError:
                    continue
            
            if not email_continue_btn:
                raise Exception("Could not find continue button to trigger email sending")
            
            log_with_timestamp("Clicking continue to trigger reset email...")
            email_continue_btn.click()
            time.sleep(5)
            
            # Step 5: Fetch reset email from Gmail
            log_with_timestamp("=== STEP 5: FETCHING FRESH RESET EMAIL FROM GMAIL ===")
            email_content, email_subject = fetch_capcut_email(EMAIL, GMAIL_APP_PASSWORD, max_wait_time=120)
            
            if not email_content:
                raise Exception("Failed to retrieve reset email from Gmail")
            
            log_with_timestamp(f"Retrieved email: {email_subject}")
            
            # Step 6: Extract reset link
            log_with_timestamp("=== STEP 6: EXTRACTING RESET LINK ===")
            reset_info = extract_reset_info(email_content)
            
            if not reset_info or reset_info["type"] != "link":
                raise Exception("No reset link found in email")
            
            reset_link = reset_info["value"]
            # Fix HTML entities in the URL
            reset_link = reset_link.replace('&amp;', '&')
            log_with_timestamp(f"Reset link URL: {reset_link}")
            
            # Step 6.5: Clear cache and cookies again before accessing reset link
            log_with_timestamp("=== STEP 6.5: CLEARING CACHE BEFORE RESET LINK ===")
            context.clear_cookies()
            log_with_timestamp("Cookies cleared before reset link")
            page.goto('about:blank')
            log_with_timestamp("Cache cleared - navigated to about:blank before reset")
            
            # Step 7: Navigate to reset link
            log_with_timestamp("=== STEP 7: NAVIGATING TO RESET LINK ===")
            page.goto(reset_link, timeout=30000)
            log_with_timestamp(f"Reset page loaded: {page.url}")
            
            # Handle cookie banner again after clearing cache
            time.sleep(2)  # Brief wait for page to render
            handle_all_banners_and_modals(page)
            
            # Now wait for network to be idle (shorter timeout)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
                log_with_timestamp("Reset page network idle achieved")
            except TimeoutError:
                log_with_timestamp("Reset page network idle timeout - proceeding anyway")
            
            # Step 8: Fill password reset form
            log_with_timestamp("=== STEP 8: FILLING PASSWORD RESET FORM ===")
            time.sleep(3)
            
            # Debug: Check what's on the page
            log_with_timestamp("Debugging: Checking page content...")
            try:
                all_inputs = page.query_selector_all('input')
                log_with_timestamp(f"Found {len(all_inputs)} input elements on page")
                
                for i, inp in enumerate(all_inputs):
                    input_type = inp.get_attribute('type') or 'text'
                    placeholder = inp.get_attribute('placeholder') or ''
                    name = inp.get_attribute('name') or ''
                    log_with_timestamp(f"Input {i+1}: type='{input_type}', placeholder='{placeholder}', name='{name}'")
            except Exception as e:
                log_with_timestamp(f"Debug failed: {e}")
            
            # Find new password field with multiple selector strategies
            log_with_timestamp("Looking for new password field...")
            new_password_selectors = [
                'input[type="password"]',  # Try generic password field first
                'input[placeholder*="password"]',
                'input[placeholder*="Password"]', 
                'input[name*="password"]',
                'input[name*="Password"]',
                'input[type="password"][placeholder="Enter new password"]',
                'input[type="password"][placeholder*="new password"]',
                'input[type="password"][placeholder*="New password"]',
                'input[placeholder*="new"]',
                'input[placeholder*="New"]'
            ]
            
            new_password_field = None
            for selector in new_password_selectors:
                try:
                    new_password_field = page.wait_for_selector(selector, timeout=5000)
                    if new_password_field and new_password_field.is_visible():
                        log_with_timestamp(f"Found new password field with selector: {selector}")
                        break
                except TimeoutError:
                    continue
            
            if new_password_field:
                log_with_timestamp(f"Filling new password: {new_password}")
                new_password_field.click()
                new_password_field.fill(new_password)
            else:
                log_with_timestamp("ERROR: Could not find new password field")
                raise Exception("New password field not found")
            
            # Find confirm password field with multiple selector strategies
            log_with_timestamp("Looking for confirm password field...")
            confirm_password_selectors = [
                'input[type="password"][placeholder="Enter new password again"]',
                'input[type="password"][placeholder*="confirm"]',
                'input[type="password"][placeholder*="Confirm"]',
                'input[type="password"][placeholder*="again"]'
            ]
            
            # Try to find a second password field
            confirm_password_field = None
            password_fields = page.query_selector_all('input[type="password"]')
            if len(password_fields) >= 2:
                confirm_password_field = password_fields[1]  # Use second password field
                log_with_timestamp("Found confirm password field (second password input)")
            else:
                for selector in confirm_password_selectors:
                    try:
                        confirm_password_field = page.wait_for_selector(selector, timeout=5000)
                        if confirm_password_field and confirm_password_field.is_visible():
                            log_with_timestamp(f"Found confirm password field with selector: {selector}")
                            break
                    except TimeoutError:
                        continue
            
            if confirm_password_field:
                log_with_timestamp("Filling confirm password...")
                confirm_password_field.click()
                confirm_password_field.fill(new_password)
            else:
                log_with_timestamp("ERROR: Could not find confirm password field")
                raise Exception("Confirm password field not found")
            
            # Find and click confirm button
            confirm_btn_selectors = [
                'button:has-text("Confirm password")',
                'button[class*="lv_forget_pwd_panel_btn"]',
                'button:has-text("Confirm")',
                'button[type="submit"]'
            ]
            
            confirm_btn = None
            for selector in confirm_btn_selectors:
                try:
                    confirm_btn = page.wait_for_selector(selector, timeout=5000)
                    log_with_timestamp(f"Found confirm button with selector: {selector}")
                    break
                except TimeoutError:
                    continue
            
            if not confirm_btn:
                raise Exception("Could not find confirm password button")
            
            log_with_timestamp("Clicking confirm password button...")
            confirm_btn.click()
            
            # Step 9: Wait for confirmation
            log_with_timestamp("=== STEP 9: WAITING FOR CONFIRMATION ===")
            time.sleep(3)
            
            current_url = page.url
            log_with_timestamp(f"Current URL after password reset: {current_url}")
            
            # Check for success
            if "login" in current_url.lower():
                log_with_timestamp("SUCCESS: Redirected to login page - password reset successful")
            else:
                log_with_timestamp("Password reset status unclear - checking for success indicators")
            
            # Step 9: Test login with new password
            log_with_timestamp("=== STEP 9: TESTING LOGIN WITH NEW PASSWORD ===")
            page.goto(LOGIN_URL, timeout=30000)
            log_with_timestamp("Page loaded for verification login")
            
            # Handle cookie banner IMMEDIATELY after page load
            time.sleep(2)  # Brief wait for page to render
            handle_all_banners_and_modals(page)
            
            # Now wait for network to be idle (shorter timeout)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
                log_with_timestamp("Page network idle achieved")
            except TimeoutError:
                log_with_timestamp("Network idle timeout - proceeding anyway")
            
            # Fill email with multiple selector strategies
            log_with_timestamp("Filling email for verification login...")
            email_selectors = [
                'input[placeholder="Enter email"]',
                'input[type="email"]',
                'input[name="email"]',
                'input[id*="email"]',
                'input[class*="email"]'
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = page.wait_for_selector(selector, timeout=5000)
                    if email_input and email_input.is_visible():
                        log_with_timestamp(f"Found email input with selector: {selector}")
                        break
                except TimeoutError:
                    continue
            
            if email_input:
                # Clear any existing content and fill email
                email_input.click()
                email_input.fill('')
                email_input.fill(EMAIL)
                log_with_timestamp(f"Email filled: {EMAIL}")
            else:
                log_with_timestamp("ERROR: Could not find email input field")
                raise Exception("Email input field not found")
            
            # Click continue
            continue_btn = page.wait_for_selector('button:has-text("Continue")', timeout=10000)
            continue_btn.click()
            time.sleep(3)
            
            # Fill new password
            log_with_timestamp("Filling new password for verification...")
            password_input = page.wait_for_selector('input[placeholder="Enter password"]', timeout=10000)
            password_input.fill(new_password)
            
            # Click login
            login_btn = page.wait_for_selector('button:has-text("Sign In")', timeout=10000)
            login_btn.click()
            
            # Check login success
            time.sleep(5)
            final_url = page.url
            
            if "my-edit" in final_url or "dashboard" in final_url:
                log_with_timestamp("SUCCESS: Login successful with new password!")
                log_with_timestamp("=== PASSWORD RESET VERIFICATION COMPLETE ===")
                log_with_timestamp(f"FINAL NEW PASSWORD: {new_password}")
                log_with_timestamp("============================================")
            else:
                log_with_timestamp("WARNING: Login with new password may have failed")
                log_with_timestamp(f"Current URL: {final_url}")
            
            # Keep browser open for observation
            log_with_timestamp("=== KEEPING BROWSER OPEN FOR 5 SECONDS ===")
            time.sleep(5)
            
        except Exception as e:
            print(f"Error occurred during login process: {e}")
            
            # Try to capture any visible error messages on the page
            try:
                page_content = page.content()
                if "error" in page_content.lower():
                    print("Page contains error-related content")
                if "captcha" in page_content.lower():
                    print("Page contains CAPTCHA-related content")
            except:
                pass
                
        finally:
            print("Closing browser...")
            browser.close()
            print("Test completed!")


if __name__ == "__main__":
    test_capcut_password_reset()
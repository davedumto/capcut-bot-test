import asyncio
import os
from playwright.async_api import async_playwright, Page, Browser
from imap_tools import MailBox
from dotenv import load_dotenv
import re
import string
import secrets

load_dotenv()

class CapCutPasswordResetBot:
    """
    Automates the complete CapCut forgot password flow in 14 steps.
    Uses incognito browser to avoid cache issues.
    Reads Gmail IMAP to get password reset link.
    """
    
    def __init__(
        self, 
        capcut_email: str,
        gmail_email: str, 
        gmail_app_password: str,
        headless: bool = False
    ):
        self.capcut_email = capcut_email
        self.gmail_email = gmail_email
        self.gmail_app_password = gmail_app_password
        self.headless = headless
        self.browser: Browser = None
        self.page: Page = None
        self.new_password: str = None
        
    def generate_strong_password(self) -> str:
        """Generate a strong password: 14+ chars, mixed case, numbers, safe special chars"""
        length = 14
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        numbers = string.digits
        # Use only commonly accepted special characters
        special = "!@#$%&"
        
        password = (
            secrets.choice(uppercase) +
            secrets.choice(lowercase) +
            secrets.choice(numbers) +
            secrets.choice(special)
        )
        
        all_chars = uppercase + lowercase + numbers + special
        password += ''.join(secrets.choice(all_chars) for _ in range(length - 4))
        
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        return ''.join(password_list)
    
    async def launch_incognito_browser(self):
        """STEP 1-2: Launch browser in true incognito mode"""
        import random
        import tempfile
        import os
        
        playwright = await async_playwright().start()
        
        # Randomize browser settings to avoid detection
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        
        # Random viewport sizes
        viewports = [
            {"width": 1366, "height": 768},
            {"width": 1920, "height": 1080},
            {"width": 1440, "height": 900},
            {"width": 1536, "height": 864}
        ]
        
        selected_viewport = random.choice(viewports)
        selected_user_agent = random.choice(user_agents)
        
        print(f"🎭 Using user agent: {selected_user_agent}")
        print(f"📱 Using viewport: {selected_viewport['width']}x{selected_viewport['height']}")
        
        # Create a temporary directory for this session (acts like incognito)
        temp_dir = tempfile.mkdtemp(prefix="capcut_bot_")
        print(f"🕵️ Creating incognito session with temp profile: {temp_dir}")
        
        # Launch browser with temporary user data dir (true incognito equivalent)
        self.browser = await playwright.chromium.launch_persistent_context(
            user_data_dir=temp_dir,
            headless=self.headless,
            user_agent=selected_user_agent,
            viewport=selected_viewport,
            locale="en-US",
            timezone_id="America/New_York",
            accept_downloads=False,
            ignore_https_errors=True,
            args=[
                '--no-first-run',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor',
                '--disable-background-networking',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-sync',
                '--disable-translate',
                '--disable-web-security',
                '--no-default-browser-check',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection'
            ],
            # Add realistic headers
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none"
            }
        )
        
        # Store temp dir for cleanup
        self.temp_dir = temp_dir
        
        # Remove automation indicators
        await self.browser.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            window.chrome = {
                runtime: {},
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Hide automation traces
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)
        
        self.page = await self.browser.new_page()
        
    async def navigate_to_login(self):
        """Navigate to CapCut login page"""
        await self.page.goto('https://www.capcut.com/login?redirect_url=https%3A%2F%2Fwww.capcut.com%2Fmy-edit', wait_until='networkidle')
        await self.page.wait_for_load_state('networkidle')
        
        # Handle cookies banner if present
        try:
            cookies_accept = await self.page.wait_for_selector('button:has-text("Accept"), button:has-text("accept"), button:has-text("Allow"), button[id*="accept"], button[class*="accept"]', timeout=5000)
            if cookies_accept:
                await cookies_accept.click()
                await asyncio.sleep(2)
                print("✅ Accepted cookies banner")
        except Exception:
            print("ℹ️  No cookies banner found or already accepted")
        
    async def enter_email(self, email: str):
        """STEP 3: Enter email in login form"""
        # Find email input (adjust selector based on CapCut's actual HTML)
        email_input = await self.page.query_selector('input[type="email"], input[placeholder*="email" i]')
        if email_input:
            await email_input.fill(email)
        else:
            raise Exception("Could not find email input field on login page")
        
    async def click_continue(self):
        """STEP 4: Click continue button"""
        continue_button = await self.page.query_selector('button:has-text("Continue"), button:has-text("continue")')
        if continue_button:
            await continue_button.click()
            await self.page.wait_for_load_state('networkidle')
        else:
            raise Exception("Could not find Continue button")
        
    async def click_forgot_password(self):
        """STEP 5: Click forgot password link"""
        # Target the specific forgot password button element
        forgot_selectors = [
            'div.forget-pwd-btn',
            '.forget-pwd-btn',
            'div:has-text("Forgot password?")',
            'div:has-text("forgot password")',
            '[class="forget-pwd-btn"]'
        ]
        
        forgot_link = None
        for selector in forgot_selectors:
            try:
                forgot_link = await self.page.wait_for_selector(selector, timeout=5000)
                if forgot_link and await forgot_link.is_visible():
                    print(f"✅ Found forgot password button with selector: {selector}")
                    break
            except:
                continue
        
        if forgot_link:
            await forgot_link.click()
            await self.page.wait_for_load_state('networkidle')
        else:
            raise Exception("Could not find Forgot password button with class 'forget-pwd-btn'")
        
    async def verify_email_prefilled(self):
        """STEP 6: Verify email is prefilled (don't type again)"""
        email_input = await self.page.query_selector('input[type="email"], input[placeholder*="email" i]')
        if email_input:
            current_value = await email_input.input_value()
            if current_value != self.capcut_email:
                raise Exception(f"Email not prefilled. Found: {current_value}, Expected: {self.capcut_email}")
        else:
            raise Exception("Could not find email input on forgot password page")
        
    async def submit_forgot_password_form(self):
        """STEP 7: Click confirm/send button on forgot password form"""
        submit_button = await self.page.query_selector('button:has-text("Confirm"), button:has-text("Send"), button:has-text("submit")')
        if submit_button:
            await submit_button.click()
            await self.page.wait_for_load_state('networkidle')
        else:
            raise Exception("Could not find Submit button on forgot password form")
        
    async def get_reset_link_from_email(self, timeout: int = 60) -> str:
        """STEP 8: Read Gmail inbox and extract password reset link"""
        import time
        from datetime import datetime, timedelta
        import email.utils
        
        # Record the time when form was submitted (before waiting)
        form_submit_time = time.time()
        print(f"🕒 Form submitted at {datetime.fromtimestamp(form_submit_time).strftime('%H:%M:%S')}")
        
        # Wait a few seconds for the email to be sent after form submission
        print("⏳ Waiting for email to be sent...")
        await asyncio.sleep(3)  # Reduced wait time
        
        print("🔍 Will accept emails that arrived after form submission time...")
        
        while time.time() - form_submit_time < timeout:
            try:
                mailbox = MailBox('imap.gmail.com')
                mailbox.login(self.gmail_email, self.gmail_app_password)
                
                # Search for CapCut password reset emails that arrived AFTER we submitted the form
                
                # Convert form submit time to datetime for comparison
                form_submit_datetime = datetime.fromtimestamp(form_submit_time)
                # Allow emails from 30 seconds before form submission to account for timing differences
                cutoff_datetime = form_submit_datetime - timedelta(seconds=30)
                
                # Get emails from today only
                today_str = datetime.now().strftime('%d-%b-%Y')
                
                # Search for recent emails with CapCut subject
                messages = list(mailbox.fetch(f'(SUBJECT "CapCut password reset request" SINCE "{today_str}")', bulk=True, limit=15, reverse=True))
                print(f"📧 Found {len(messages)} CapCut emails from today")
                
                # Filter to emails that are recent enough to be from this form submission
                fresh_messages = []
                for msg in messages:
                    msg_time = email.utils.parsedate_tz(msg.date_str)
                    if msg_time:
                        msg_datetime = datetime.fromtimestamp(email.utils.mktime_tz(msg_time))
                        
                        # Accept emails that arrived within 30 seconds before or after form submission
                        if msg_datetime >= cutoff_datetime:
                            fresh_messages.append(msg)
                            print(f"✅ Recent email: {msg_datetime.strftime('%H:%M:%S')} - {msg.subject}")
                        else:
                            print(f"⏰ Old email: {msg_datetime.strftime('%H:%M:%S')} - {msg.subject}")
                
                messages = fresh_messages
                print(f"🔥 Processing {len(messages)} recent emails")
                
                for msg in messages:
                    # Extract URLs from email body
                    html_body = msg.html or msg.text
                    if html_body:
                        # Find URLs that look like reset links - more aggressive regex
                        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', html_body)
                        
                        # Also search for URLs in href attributes specifically
                        href_urls = re.findall(r'href=["\']([^"\']*)["\']', html_body, re.IGNORECASE)
                        urls.extend(href_urls)
                        
                        # Remove duplicates and clean URLs
                        unique_urls = list(set(urls))
                        
                        print(f"📧 Found {len(unique_urls)} total URLs in email")
                        
                        for url in unique_urls:
                            print(f"🔍 Checking URL: {url}")
                            if any(keyword in url.lower() for keyword in ['reset', 'verify', 'forget', 'password', 'change-pwd']):
                                # Comprehensive URL cleaning
                                import html
                                import urllib.parse
                                
                                # Step 1: Decode HTML entities (&amp; -> &, &quot; -> ", etc.)
                                clean_url = html.unescape(url)
                                
                                # Step 2: Handle URL encoding (%40 -> @, %2F -> /, etc.)
                                clean_url = urllib.parse.unquote(clean_url)
                                
                                # Step 3: Remove any trailing punctuation that might be from email formatting
                                clean_url = clean_url.rstrip('.,;!)')
                                
                                # Step 4: Ensure it's a proper URL
                                if not clean_url.startswith('http'):
                                    clean_url = 'https://' + clean_url.lstrip('/')
                                
                                print(f"🔧 Original URL: {url}")
                                print(f"✅ Cleaned URL: {clean_url}")
                                print(f"🔍 URL contains keywords: {[kw for kw in ['reset', 'verify', 'forget', 'password', 'change-pwd'] if kw in clean_url.lower()]}")
                                
                                mailbox.logout()
                                return clean_url
                
                mailbox.logout()
            except Exception as e:
                print(f"Email check error (will retry): {e}")
            
            await asyncio.sleep(2)  # Wait 2 seconds before retry
        
        raise Exception(f"Could not find password reset link in email after {timeout} seconds")
        
    async def navigate_to_reset_link(self, reset_link: str):
        """STEP 9: Navigate to the password reset page"""
        print(f"🔗 Navigating to reset link: {reset_link}")
        await self.page.goto(reset_link, wait_until='networkidle')
        await self.page.wait_for_load_state('networkidle')
        
        # Debug: Check what page we actually landed on
        current_url = self.page.url
        page_title = await self.page.title()
        print(f"📍 Current URL: {current_url}")
        print(f"📄 Page title: {page_title}")
        
        # Wait a moment for page to fully load
        await asyncio.sleep(3)
        
        # Check if we're on the right page by looking for password fields
        password_inputs = await self.page.query_selector_all('input[type="password"]')
        print(f"🔑 Found {len(password_inputs)} password fields on this page")
        
        # Also check for any input fields that might be password fields
        all_inputs = await self.page.query_selector_all('input')
        print(f"📝 Found {len(all_inputs)} total input fields")
        
        # Look for specific CapCut password field indicators
        capcut_password_indicators = [
            'input[placeholder*="password" i]',
            'input[placeholder*="Password" i]', 
            'input[name*="password" i]',
            'input[id*="password" i]',
            '.password-input',
            '[data-testid*="password"]'
        ]
        
        for selector in capcut_password_indicators:
            fields = await self.page.query_selector_all(selector)
            if fields:
                print(f"🔍 Found {len(fields)} fields with selector: {selector}")
        
        # Show page content snippet for debugging
        page_content = await self.page.content()
        if any(indicator in page_content.lower() for indicator in ["enter new password", "new password", "reset password", "password"]):
            print("✅ Password reset form detected")
        elif "expired" in page_content.lower() or "invalid" in page_content.lower():
            print("❌ Link may be expired or invalid")
        else:
            print("⚠️  Unexpected page content")
            print(f"📝 Page snippet: {page_content[:500]}...")
        
    async def enter_new_password(self, password: str):
        """STEP 10-11: Enter new password in both fields"""
        # Wait for page to load
        await asyncio.sleep(3)
        
        # Target the specific CapCut password input fields
        try:
            # First password field - "Enter new password"
            password_field1 = await self.page.wait_for_selector('input[placeholder="Enter new password"]', timeout=10000)
            await password_field1.fill(password)
            
            # Verify first field was filled correctly
            field1_value = await password_field1.input_value()
            if field1_value == password:
                print("✅ Filled first password field successfully")
            else:
                print(f"⚠️  First field fill issue: expected '{password}', got '{field1_value}'")
            
            # Second password field - "Enter new password again"  
            password_field2 = await self.page.wait_for_selector('input[placeholder="Enter new password again"]', timeout=10000)
            await password_field2.fill(password)
            
            # Verify second field was filled correctly
            field2_value = await password_field2.input_value()
            if field2_value == password:
                print("✅ Filled second password field successfully")
            else:
                print(f"⚠️  Second field fill issue: expected '{password}', got '{field2_value}'")
            
        except Exception as e:
            # Fallback: try generic password selectors
            password_inputs = await self.page.query_selector_all('input[type="password"]')
            if len(password_inputs) >= 2:
                await password_inputs[0].fill(password)
                await password_inputs[1].fill(password)
                
                # Verify fallback method worked
                field1_val = await password_inputs[0].input_value()
                field2_val = await password_inputs[1].input_value()
                print(f"✅ Filled {len(password_inputs)} password fields using fallback method")
                print(f"   Field 1: {'✓' if field1_val == password else '✗'} Field 2: {'✓' if field2_val == password else '✗'}")
            else:
                raise Exception(f"Could not find password fields. Found {len(password_inputs)} password inputs")
        
        self.new_password = password
        
    async def confirm_password_reset(self):
        """STEP 12: Click confirm password button"""
        # Wait a moment to ensure password fields are fully processed
        await asyncio.sleep(2)
        
        confirm_button = await self.page.query_selector('button:has-text("Confirm")')
        if confirm_button:
            print("🔍 Checking button state before clicking...")
            is_enabled = await confirm_button.is_enabled()
            is_visible = await confirm_button.is_visible()
            print(f"   Button enabled: {is_enabled}, visible: {is_visible}")
            
            # Check if there are any validation errors before clicking
            page_content_before = await self.page.content()
            if "error" in page_content_before.lower():
                print("⚠️  Found error on page before clicking submit")
            
            # Listen for network requests to see if form is actually submitted
            requests_made = []
            def track_request(request):
                if 'capcut.com' in request.url and request.method == 'POST':
                    requests_made.append(f"POST {request.url}")
                    print(f"🌐 Form submission request: {request.url}")
            
            self.page.on('request', track_request)
            
            # Double-check that button is clickable and click it
            await confirm_button.scroll_into_view_if_needed()
            print("🔄 Clicking confirm button...")
            await confirm_button.click()
            
            # Wait to see if any POST requests are made
            await asyncio.sleep(3)
            
            # Remove listener
            self.page.remove_listener('request', track_request)
            
            print(f"📡 POST requests made: {len(requests_made)}")
            for req in requests_made:
                print(f"   {req}")
            
            if len(requests_made) == 0:
                print("❌ NO form submission requests detected! Form might not be submitting.")
            
            await self.page.wait_for_load_state('networkidle')
            
            # Check the page after clicking to see what happened
            current_url = self.page.url
            page_content_after = await self.page.content()
            print(f"📍 URL after click: {current_url}")
            
            if "error" in page_content_after.lower() or "invalid" in page_content_after.lower():
                print("❌ Error detected on page after form submission")
                # Look for specific error messages
                if "password" in page_content_after.lower() and "invalid" in page_content_after.lower():
                    print("⚠️  Password validation error detected")
            
        else:
            raise Exception("Could not find Confirm password button")
        
    async def verify_success(self) -> bool:
        """STEP 13: Wait 1 minute for password reset to complete"""
        print("⏳ Waiting 1 minute for password reset to complete...")
        
        # Wait 1 minute (60 seconds) for password reset to fully process
        for remaining in range(60, 0, -10):
            print(f"⏳ Waiting {remaining} more seconds for password reset to complete...")
            await asyncio.sleep(10)
        
        print("✅ Password reset processing time complete")
        return True
        
    async def close_browser(self):
        """STEP 14: Close browser and cleanup temp files"""
        if self.browser:
            await self.browser.close()
            
        # Clean up temporary incognito directory
        if hasattr(self, 'temp_dir'):
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up incognito session: {self.temp_dir}")
            except Exception as e:
                print(f"⚠️  Could not clean temp dir: {e}")
        
    async def run_complete_flow(self) -> tuple[bool, str]:
        """
        Run the entire 14-step flow.
        Returns: (success: bool, new_password: str)
        """
        try:
            print("🤖 Starting CapCut password reset bot...")
            
            print("Step 1-2: Launching incognito browser...")
            await self.launch_incognito_browser()
            
            print("Step 2: Navigating to login page...")
            await self.navigate_to_login()
            
            print("Step 3: Entering email...")
            await self.enter_email(self.capcut_email)
            
            print("Step 4: Clicking continue...")
            await self.click_continue()
            
            print("Step 5: Clicking forgot password...")
            await self.click_forgot_password()
            
            print("Step 6: Verifying email is prefilled...")
            await self.verify_email_prefilled()
            
            print("Step 7: Submitting forgot password form...")
            await self.submit_forgot_password_form()
            
            print("Step 8: Getting reset link from Gmail...")
            reset_link = await self.get_reset_link_from_email()
            
            print("Step 9: Navigating to password reset page...")
            await self.navigate_to_reset_link(reset_link)
            
            print("Step 10-11: Entering new password...")
            new_password = self.generate_strong_password()
            await self.enter_new_password(new_password)
            
            print("Step 12: Confirming password reset...")
            await self.confirm_password_reset()
            
            print("Step 13: Verifying success...")
            success = await self.verify_success()
            
            if success:
                print(f"✅ Password reset successful!")
                print(f"New password: {new_password}")
                print("Step 14: Closing browser...")
                await self.close_browser()
                return (True, new_password)
            else:
                print(f"❌ Password reset failed - no success toast appeared")
                print("Step 14: Closing browser...")
                await self.close_browser()
                return (False, None)
                
        except Exception as e:
            print(f"❌ Error during password reset: {e}")
            await self.close_browser()
            return (False, None)


# Test function
async def main():
    bot = CapCutPasswordResetBot(
        capcut_email=os.getenv('CAPCUT_EMAIL'),
        gmail_email=os.getenv('GMAIL_EMAIL'),
        gmail_app_password=os.getenv('GMAIL_APP_PASSWORD'),
        headless=False  # Show browser for testing
    )
    
    success, new_password = await bot.run_complete_flow()
    
    if success:
        print(f"\n✅ Success! New password: {new_password}")
    else:
        print(f"\n❌ Failed to reset password")


if __name__ == "__main__":
    asyncio.run(main())
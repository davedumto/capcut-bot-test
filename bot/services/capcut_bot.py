# THIS IS THE MAIN BOT FILE - 11 STEP FORGOT PASSWORD FLOW
# See the BOT_FORGOT_PASSWORD_FLOW_PROMPT.md file for complete implementation
# This file contains: reset_password_forgot_flow() async function

import asyncio
import time
import logging
import random
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError
from .gmail_handler import get_capcut_reset_link
from .password_generator import generate_strong_password
from config import settings

logger = logging.getLogger(__name__)


async def reset_password_forgot_flow(email: str, new_password: str) -> dict:
    """
    Reset CapCut password using forgot password flow (11 steps)
    
    This is the main function called by the FastAPI endpoint.
    It follows the complete forgot password flow as specified in the prompt.
    
    Args:
        email: The CapCut account email
        new_password: The new password to set
        
    Returns:
        dict: {"success": bool, "message": str}
    """
    try:
        logger.info(f"Starting forgot password flow for {email}")
        
        async with async_playwright() as p:
            # Launch browser with stealth options
            browser = await p.chromium.launch(
                headless=settings.HEADLESS,
                args=[
                    '--headless=new',  # Use new headless mode
                    '--no-first-run',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-extensions',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-gpu-sandbox',
                    '--disable-software-rasterizer',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-ipc-flooding-protection',
                    '--disable-dbus',
                    '--disable-crash-reporter',
                    '--disable-in-process-stack-traces',
                    '--disable-logging',
                    '--disable-login-animations',
                    '--disable-background-networking',
                    '--disable-default-apps',
                    '--single-process'
                ]
            )
            
            # Create stealth context
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080},
                locale='en-US'
            )
            
            page = await context.new_page()
            
            try:
                # Step 1: Clear browser cache and cookies for clean state
                logger.info("Step 1: Clearing browser cache and cookies")
                await context.clear_cookies()
                await page.goto('about:blank')
                await asyncio.sleep(2)
                
                # Step 2: Navigate to CapCut login page
                logger.info("Step 2: Navigating to CapCut login page")
                login_url = "https://www.capcut.com/login"
                await page.goto(login_url, timeout=60000, wait_until='networkidle')
                await asyncio.sleep(5)
                
                # Log page content for debugging
                page_title = await page.title()
                logger.info(f"Page title: {page_title}")
                
                # Step 3: Fill email field - try multiple selectors
                logger.info("Step 3: Filling email field")
                email_selectors = [
                    'input[placeholder="Enter email"]',
                    'input[placeholder="Email"]',
                    'input[type="email"]',
                    'input[name="email"]',
                    'input[id="email"]',
                    '#email-input',
                    '.email-input input',
                    'input[placeholder*="email" i]',
                    'input[placeholder*="Email" i]',
                    'input[data-testid="email-input"]',
                ]
                
                email_input = None
                for selector in email_selectors:
                    try:
                        logger.info(f"Trying selector: {selector}")
                        email_input = await page.wait_for_selector(selector, timeout=5000)
                        if email_input and await email_input.is_visible():
                            logger.info(f"Found email input with selector: {selector}")
                            break
                        email_input = None
                    except TimeoutError:
                        continue
                
                if not email_input:
                    # Log page HTML for debugging
                    page_content = await page.content()
                    logger.error(f"Could not find email input. Page HTML snippet: {page_content[:2000]}")
                    
                    # Try to find any visible input
                    all_inputs = await page.query_selector_all('input')
                    logger.info(f"Found {len(all_inputs)} input elements on page")
                    for i, inp in enumerate(all_inputs[:5]):
                        inp_type = await inp.get_attribute('type')
                        inp_placeholder = await inp.get_attribute('placeholder')
                        inp_name = await inp.get_attribute('name')
                        logger.info(f"Input {i}: type={inp_type}, placeholder={inp_placeholder}, name={inp_name}")
                    
                    raise Exception("Could not find email input field on CapCut login page")
                
                await email_input.click()
                await asyncio.sleep(0.5)
                await email_input.fill('')
                await email_input.type(email, delay=50)  # Type slowly like a human
                await asyncio.sleep(1)
                
                # Step 4: Click Continue button
                logger.info("Step 4: Clicking Continue button")
                continue_selectors = [
                    'button:has-text("Continue")',
                    'button:has-text("Next")',
                    'button:has-text("Sign in")',
                    'button[type="submit"]',
                    '.continue-btn',
                    '.next-btn',
                ]
                
                continue_btn = None
                for selector in continue_selectors:
                    try:
                        continue_btn = await page.wait_for_selector(selector, timeout=5000)
                        if continue_btn and await continue_btn.is_visible():
                            logger.info(f"Found continue button with selector: {selector}")
                            break
                        continue_btn = None
                    except TimeoutError:
                        continue
                
                if not continue_btn:
                    raise Exception("Could not find Continue button")
                
                await continue_btn.click()
                await asyncio.sleep(5)
                
                # Step 5: Click Forgot Password
                logger.info("Step 5: Clicking Forgot Password")
                forgot_password_selectors = [
                    'div.forget-pwd-btn',
                    '.forget-pwd-btn',
                    'button:has-text("Forgot password?")',
                    'a:has-text("Forgot password?")',
                    'span:has-text("Forgot password?")',
                    'div:has-text("Forgot password?")',
                    '[class*="forgot"]',
                    'a[href*="forgot"]',
                    ':text("Forgot password")',
                ]
                
                forgot_btn = None
                for selector in forgot_password_selectors:
                    try:
                        forgot_btn = await page.wait_for_selector(selector, timeout=5000)
                        if forgot_btn and await forgot_btn.is_visible():
                            logger.info(f"Found forgot password with selector: {selector}")
                            break
                        forgot_btn = None
                    except TimeoutError:
                        continue
                
                if not forgot_btn:
                    raise Exception("Could not find forgot password button")
                
                await forgot_btn.click()
                await asyncio.sleep(3)
                
                # Step 6: Confirm forgot password request
                logger.info("Step 6: Confirming forgot password request")
                confirm_selectors = [
                    'button:has-text("Confirm")',
                    'button:has-text("Send")',
                    'button:has-text("Submit")',
                    'button:has-text("Reset")',
                    'button[type="submit"]'
                ]
                
                confirm_btn = None
                for selector in confirm_selectors:
                    try:
                        confirm_btn = await page.wait_for_selector(selector, timeout=5000)
                        if confirm_btn and await confirm_btn.is_visible():
                            logger.info(f"Found confirm button with selector: {selector}")
                            break
                        confirm_btn = None
                    except TimeoutError:
                        continue
                
                if not confirm_btn:
                    raise Exception("Could not find confirm button")
                
                await confirm_btn.click()
                await asyncio.sleep(5)
                
                # Step 7: Fetch reset email from Gmail using IMAP
                logger.info("Step 7: Fetching reset email from Gmail")
                reset_link = get_capcut_reset_link(settings.GMAIL_EMAIL, settings.GMAIL_APP_PASSWORD)
                
                if not reset_link:
                    raise Exception("Could not fetch reset email or extract reset link")
                
                logger.info(f"Got reset link: {reset_link}")
                
                # Step 8: Clear cache again before navigating to reset link
                logger.info("Step 8: Clearing cache before reset link navigation")
                await context.clear_cookies()
                await page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
                await page.goto('about:blank')
                await asyncio.sleep(2)
                
                # Step 9: Navigate to reset link
                logger.info("Step 9: Navigating to reset link")
                await page.goto(reset_link, timeout=60000, wait_until='networkidle')
                await asyncio.sleep(5)
                
                # Step 10: Fill new password
                logger.info("Step 10: Filling new password")
                await asyncio.sleep(5)
                
                password_selectors = [
                    'input[placeholder="Enter new password"]',
                    'input[placeholder*="password" i]',
                    'input[type="password"]',
                    'input[name="password"]',
                    'input[name="new_password"]',
                ]
                
                password_inputs = []
                for selector in password_selectors:
                    try:
                        inputs = await page.query_selector_all(selector)
                        for input_elem in inputs:
                            if await input_elem.is_visible():
                                password_inputs.append(input_elem)
                    except:
                        continue
                
                if len(password_inputs) >= 2:
                    await password_inputs[0].fill(new_password)
                    await asyncio.sleep(0.5)
                    await password_inputs[1].fill(new_password)
                elif len(password_inputs) == 1:
                    await password_inputs[0].fill(new_password)
                else:
                    raise Exception("Could not find password input fields")
                
                await asyncio.sleep(1)
                
                # Step 11: Submit password reset
                logger.info("Step 11: Submitting password reset")
                submit_selectors = [
                    'button:has-text("Submit")',
                    'button:has-text("Reset")',
                    'button:has-text("Confirm")',
                    'button:has-text("Save")',
                    'button[type="submit"]'
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_btn = await page.wait_for_selector(selector, timeout=5000)
                        if submit_btn and await submit_btn.is_visible():
                            await submit_btn.click()
                            logger.info(f"Clicked submit with selector: {selector}")
                            break
                    except TimeoutError:
                        continue
                
                await asyncio.sleep(5)
                
                logger.info("Password reset flow completed successfully")
                return {"success": True, "message": "Password reset successfully"}
                
            finally:
                await browser.close()
                
    except Exception as e:
        error_msg = f"Password reset failed: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}


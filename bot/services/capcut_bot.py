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
                    '--no-first-run',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-extensions'
                ]
            )
            
            # Create stealth context
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
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
                await page.goto(login_url, timeout=30000)
                await asyncio.sleep(3)
                
                # Step 3: Fill email field
                logger.info("Step 3: Filling email field")
                email_input = await page.wait_for_selector('input[placeholder="Enter email"]', timeout=10000)
                await email_input.click()
                await email_input.fill('')
                await email_input.fill(email)
                
                # Step 4: Click Continue button
                logger.info("Step 4: Clicking Continue button")
                continue_btn = await page.wait_for_selector('button:has-text("Continue")', timeout=10000)
                await continue_btn.click()
                await asyncio.sleep(3)
                
                # Step 5: Click Forgot Password
                logger.info("Step 5: Clicking Forgot Password")
                forgot_password_selectors = [
                    'div.forget-pwd-btn',
                    '.forget-pwd-btn',
                    'button:has-text("Forgot password?")',
                    'a:has-text("Forgot password?")'
                ]
                
                forgot_btn = None
                for selector in forgot_password_selectors:
                    try:
                        forgot_btn = await page.wait_for_selector(selector, timeout=5000)
                        if forgot_btn and await forgot_btn.is_visible():
                            break
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
                    'button[type="submit"]'
                ]
                
                confirm_btn = None
                for selector in confirm_selectors:
                    try:
                        confirm_btn = await page.wait_for_selector(selector, timeout=5000)
                        if confirm_btn and await confirm_btn.is_visible():
                            break
                    except TimeoutError:
                        continue
                
                if not confirm_btn:
                    raise Exception("Could not find confirm button")
                
                await confirm_btn.click()
                await asyncio.sleep(5)
                
                # Step 7: Fetch reset email from Gmail using IMAP
                logger.info("Step 7: Fetching reset email from Gmail")
                reset_link = get_capcut_reset_link(email, settings.GMAIL_APP_PASSWORD)
                
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
                await page.goto(reset_link, timeout=30000)
                await asyncio.sleep(5)
                
                # Step 10: Fill new password
                logger.info("Step 10: Filling new password")
                # Wait for dynamic content to load
                await asyncio.sleep(5)
                
                password_selectors = [
                    'input[placeholder="Enter new password"]',
                    'input[type="password"]',
                    'input[placeholder*="password"]',
                    'input[placeholder*="Password"]'
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
                    # Fill both password fields
                    await password_inputs[0].fill(new_password)
                    await password_inputs[1].fill(new_password)
                elif len(password_inputs) == 1:
                    await password_inputs[0].fill(new_password)
                else:
                    raise Exception("Could not find password input fields")
                
                # Step 11: Submit password reset
                logger.info("Step 11: Submitting password reset")
                submit_selectors = [
                    'button:has-text("Submit")',
                    'button:has-text("Reset")',
                    'button:has-text("Confirm")'
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_btn = await page.wait_for_selector(selector, timeout=5000)
                        if submit_btn:
                            await submit_btn.click()
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

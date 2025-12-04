import asyncio
import os
from bot import CapCutPasswordResetBot
from dotenv import load_dotenv

load_dotenv()

async def test_bot():
    """Test the bot locally"""
    print("=" * 50)
    print("CapCut Password Reset Bot - Test")
    print("=" * 50)
    
    bot = CapCutPasswordResetBot(
        capcut_email=os.getenv('CAPCUT_EMAIL'),
        gmail_email=os.getenv('GMAIL_EMAIL'),
        gmail_app_password=os.getenv('GMAIL_APP_PASSWORD'),
        headless=False  # Show browser while testing
    )
    
    success, new_password = await bot.run_complete_flow()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ PASSWORD RESET SUCCESSFUL!")
        print(f"New Password: {new_password}")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Try logging into CapCut with the new password")
        print("2. Verify login works")
        print("3. Then we'll integrate with scheduler")
    else:
        print("❌ PASSWORD RESET FAILED")
        print("=" * 50)
        print("\nDEBUG:")
        print("- Check browser was launched")
        print("- Verify CapCut selectors match current UI")
        print("- Check Gmail credentials are correct")
        print("- Verify reset email arrived in Gmail")

if __name__ == "__main__":
    asyncio.run(test_bot())
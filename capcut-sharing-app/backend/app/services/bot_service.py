"""
Bot service client for communicating with CapCut bot
As specified in instructions.md
"""

import httpx
from typing import Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class BotServiceClient:
    def __init__(self):
        self.base_url = settings.bot_service_url
        self.timeout = 60.0  # Bot operations can take time

    async def logout_user(self, email: str) -> Dict[str, Any]:
        """
        Call POST /bot/logout to force logout user from CapCut
        As specified in instructions.md Bot Service Endpoints
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/bot/logout",
                    json={"email": email}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully logged out user: {email}")
                    return result
                else:
                    error_msg = f"Bot logout failed: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {"success": False, "message": error_msg}
                    
        except Exception as e:
            error_msg = f"Bot logout request failed: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    async def reset_password(self, email: str, new_password: str = None) -> Dict[str, Any]:
        """
        Call POST /bot/reset-password to reset CapCut password
        As specified in instructions.md Bot Service Endpoints
        
        Args:
            email: The CapCut account email
            new_password: Optional - if not provided, bot will generate one
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {"email": email}
                if new_password:
                    payload["new_password"] = new_password
                
                response = await client.post(
                    f"{self.base_url}/bot/reset-password",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully reset password for: {email}")
                    return result
                else:
                    error_msg = f"Bot password reset failed: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {"success": False, "message": error_msg}
                    
        except Exception as e:
            error_msg = f"Bot password reset request failed: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    async def health_check(self) -> Dict[str, Any]:
        """Check if bot service is running"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    logger.info("Bot service is healthy")
                    return {"success": True, "message": "Bot service is healthy"}
                else:
                    error_msg = f"Bot service unhealthy: {response.status_code}"
                    logger.warning(error_msg)
                    return {"success": False, "message": error_msg}
                    
        except Exception as e:
            error_msg = f"Bot service health check failed: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}


# Singleton instance
bot_service = BotServiceClient()
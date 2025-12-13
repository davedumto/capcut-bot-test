"""
HTTPS Enforcement Middleware (Production Only)
Redirects HTTP requests to HTTPS in production environments
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from app.core.config import settings


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce HTTPS in production"""
    
    async def dispatch(self, request: Request, call_next):
        # Only enforce HTTPS in production
        if settings.is_production():
            # Check if request is not already HTTPS
            if request.url.scheme != "https":
                # Get the HTTPS version of the URL
                https_url = request.url.replace(scheme="https")
                # Redirect to HTTPS
                return RedirectResponse(url=str(https_url), status_code=301)
        
        # Continue with the request
        response = await call_next(request)
        return response

"""
Security Headers Middleware
Adds security headers to all HTTP responses to prevent common web attacks
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # X-Content-Type-Options: Prevents MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options: Prevents clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-XSS-Protection: Enables browser XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy: Controls how much referrer information is shared
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content-Security-Policy: Controls which resources can be loaded
        csp = self._get_csp_header()
        if csp:
            response.headers["Content-Security-Policy"] = csp
        
        # HTTP Strict Transport Security (HSTS): Force HTTPS in production
        if settings.is_production():
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Permissions-Policy: Control browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
    
    def _get_csp_header(self) -> str:
        """Generate Content Security Policy header"""
        if settings.is_development():
            # Relaxed CSP for development
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' http://localhost:* ws://localhost:*;"
            )
        else:
            # Strict CSP for production
            return (
                "default-src 'self'; "
                f"script-src 'self' {settings.frontend_url}; "
                f"style-src 'self' {settings.frontend_url} 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                f"connect-src 'self' {settings.frontend_url} https:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )

"""
Rate Limiting Middleware
Prevents API abuse and DDoS attacks using SlowAPI
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from app.core.config import settings


# Function to get identifier for rate limiting
def get_identifier(request: Request) -> str:
    """Get unique identifier for rate limiting (IP + user if authenticated)"""
    # Use IP address as primary identifier
    identifier = get_remote_address(request)
    
    # If user is authenticated, add user ID for more specific limiting
    # This prevents a single user from bypassing limits by changing IPs
    if hasattr(request.state, "user_id"):
        identifier = f"{identifier}:user_{request.state.user_id}"
    
    return identifier


# Create limiter instance
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["200/minute"] if settings.is_development() else ["100/minute"],
    enabled=True
)

# Rate limit configurations per endpoint type
RATE_LIMITS = {
    "auth_login": "5/minute",  # Strict for login attempts
    "auth_magic_link": "3/hour",  # Magic link requests
    "password_reset": "3/hour",  # Password reset requests  
    "payment": "10/hour",  # Payment operations
    "booking": "20/hour",  # Booking operations
    "general_api": "100/minute",  # General API calls
    "public": "200/minute" if settings.is_development() else "150/minute",  # Public endpoints
}


def get_rate_limit(endpoint_type: str) -> str:
    """Get rate limit for specific endpoint type"""
    return RATE_LIMITS.get(endpoint_type, RATE_LIMITS["general_api"])
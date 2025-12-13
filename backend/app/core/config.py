from pydantic_settings import BaseSettings
from pydantic import field_validator, ValidationInfo
from typing import Optional
import secrets
import sys


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Services
    bot_service_url: str = "http://localhost:5000"
    frontend_url: str = "http://localhost:3000"
    
    # Security
    secret_key: str
    admin_email: str = "admin@slotio.com"
    admin_password: str  # Must be set via environment variable
    
    # Email
    gmail_user: str
    gmail_app_password: str
    
    # Payment
    paystack_secret_key: str
    paystack_public_key: str
    
    # Environment
    environment: str = "development"
    
    # Bot Workers - Scalability config
    max_concurrent_bots: int = 3  # Increase as you add more RAM
    
    class Config:
        env_file = ".env"
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo) -> str:
        """Validate SECRET_KEY is strong enough"""
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        
        # Check for weak/default values
        weak_secrets = ['default', 'secret', 'password', 'changeme', '12345']
        if any(weak in v.lower() for weak in weak_secrets):
            raise ValueError('SECRET_KEY appears to be a weak/default value')
        
        return v
    
    @field_validator('admin_password')
    @classmethod
    def validate_admin_password(cls, v: str, info: ValidationInfo) -> str:
        """Validate admin password strength"""
        if len(v) < 12:
            raise ValueError('ADMIN_PASSWORD must be at least 12 characters long')
        
        # Check for weak passwords
        weak_passwords = ['admin123', 'password', 'admin', '12345678']
        if v.lower() in weak_passwords:
            raise ValueError('ADMIN_PASSWORD is too weak. Use a strong password')
        
        return v
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value"""
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f'ENVIRONMENT must be one of: {", ".join(allowed)}')
        return v
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == 'production'
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == 'development'
    
    def get_cors_origins(self) -> list[str]:
        """Get CORS origins based on environment"""
        if self.is_production():
            # In production, only allow frontend URL
            return [self.frontend_url]
        else:
            # In development, allow localhost
            return [
                self.frontend_url,
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000"
            ]
    
    def validate_production_config(self) -> dict[str, str]:
        """Validate configuration is safe for production"""
        warnings = []
        errors = []
        
        if self.is_production():
            # Check for localhost URLs in production
            if 'localhost' in self.frontend_url.lower():
                errors.append('FRONTEND_URL must not be localhost in production')
            
            if 'localhost' in self.database_url.lower():
                errors.append('DATABASE_URL must not be localhost in production')
            
            # Check Paystack is using live keys
            if self.paystack_secret_key.startswith('sk_test_'):
                warnings.append('Using Paystack TEST keys in production')
            
            if not self.paystack_secret_key.startswith('sk_live_'):
                errors.append('PAYSTACK_SECRET_KEY must use live key (sk_live_) in production')
            
            # Validate HTTPS in production
            if not self.frontend_url.startswith('https://'):
                warnings.append('FRONTEND_URL should use HTTPS in production')
        
        return {
            'environment': self.environment,
            'warnings': warnings,
            'errors': errors,
            'status': 'error' if errors else ('warning' if warnings else 'ok')
        }


def log_security_status(settings_obj: Settings):
    """Log security configuration status without exposing secrets"""
    validation = settings_obj.validate_production_config()
    
    print("\n" + "=" * 60)
    print("🔒 SECURITY CONFIGURATION STATUS")
    print("=" * 60)
    print(f"Environment: {validation['environment']}")
    print(f"Status: {validation['status'].upper()}")
    print(f"Secret Key: {'✅ Set (' + str(len(settings_obj.secret_key)) + ' chars)'}")
    print(f"Admin Password: {'✅ Set (' + str(len(settings_obj.admin_password)) + ' chars)'}")
    print(f"Database: {'✅ Configured'}")
    print(f"Paystack: {'✅ Configured'}")
    print(f"Gmail: {'✅ Configured'}")
    
    if validation['errors']:
        print("\n🚨 ERRORS:")
        for error in validation['errors']:
            print(f"  ❌ {error}")
    
    if validation['warnings']:
        print("\n⚠️  WARNINGS:")
        for warning in validation['warnings']:
            print(f"  ⚠️  {warning}")
    
    print("=" * 60 + "\n")
    
    # Fail fast if errors in production
    if validation['errors'] and settings_obj.is_production():
        print("💥 CRITICAL: Cannot start in production with configuration errors!")
        sys.exit(1)


def generate_secret_key(length: int = 64) -> str:
    """Generate a cryptographically secure secret key"""
    return secrets.token_urlsafe(length)


# Initialize settings
try:
    settings = Settings()
    log_security_status(settings)
except Exception as e:
    print(f"\n💥 CONFIGURATION ERROR: {e}\n")
    print("Please check your .env file and ensure all required variables are set.")
    print("\nRequired variables:")
    print("  - DATABASE_URL")
    print("  - SECRET_KEY (min 32 chars)")
    print("  - ADMIN_EMAIL")
    print("  - ADMIN_PASSWORD (min 12 chars)")
    print("  - GMAIL_USER")
    print("  - GMAIL_APP_PASSWORD")
    print("  - PAYSTACK_SECRET_KEY")
    print("  - PAYSTACK_PUBLIC_KEY")
    print("\nTo generate a strong SECRET_KEY, run:")
    print("  python -c 'import secrets; print(secrets.token_urlsafe(64))'")
    print()
    sys.exit(1)
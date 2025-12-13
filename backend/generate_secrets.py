#!/usr/bin/env python3
"""
Generate secure secrets for CapCut Sharing Platform
Run this script to generate strong random secrets for your .env file
"""

import secrets
import string


def generate_secret_key(length=64):
    """Generate a URL-safe secret key"""
    return secrets.token_urlsafe(length)


def generate_password(length=20, use_special=True):
    """Generate a strong password"""
    chars = string.ascii_letters + string.digits
    if use_special:
        chars += string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_database_password(length=32):
    """Generate a strong database password (alphanumeric only)"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def main():
    print("\n" + "=" * 60)
    print("🔐 SECRET GENERATOR")
    print("=" * 60)
    print("\nGenerate strong secrets for your .env file:\n")
    
    print("# SECRET_KEY (for JWT tokens and session encryption)")
    print(f"SECRET_KEY={generate_secret_key()}\n")
    
    print("# ADMIN_PASSWORD (for admin dashboard login)")
    print(f"ADMIN_PASSWORD={generate_password(20)}\n")
    
    print("# DATABASE_PASSWORD (for PostgreSQL)")
    print(f"DATABASE_PASSWORD={generate_database_password()}\n")
    
    print("=" * 60)
    print("Copy the values above to your .env file")
    print("⚠️  Never commit these values to git!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

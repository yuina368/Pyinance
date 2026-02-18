#!/usr/bin/env python3
"""
Tests for authentication service
"""

import pytest
from app.services.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token,
    authenticate_user
)


def test_password_hashing():
    """Test password hashing and verification"""
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    # Hash should be different from original password
    assert hashed != password
    
    # Verify should return True for correct password
    assert verify_password(password, hashed) is True
    
    # Verify should return False for incorrect password
    assert verify_password("wrong_password", hashed) is False


def test_access_token_creation():
    """Test JWT access token creation"""
    data = {"sub": "testuser", "role": "user"}
    token = create_access_token(data)
    
    # Token should be a string
    assert isinstance(token, str)
    
    # Token should not be empty
    assert len(token) > 0


def test_token_verification():
    """Test JWT token verification"""
    data = {"sub": "testuser", "role": "admin"}
    token = create_access_token(data)
    
    # Verify token
    payload = verify_token(token)
    
    # Payload should contain original data
    assert payload["sub"] == "testuser"
    assert payload["role"] == "admin"
    assert "exp" in payload  # Expiration time


def test_user_authentication():
    """Test user authentication"""
    # Test valid credentials
    user = authenticate_user("admin", "admin123")
    assert user is not None
    assert user["username"] == "admin"
    assert user["role"] == "admin"
    
    # Test invalid username
    user = authenticate_user("nonexistent", "admin123")
    assert user is None
    
    # Test invalid password
    user = authenticate_user("admin", "wrongpassword")
    assert user is None


def test_user_authentication_demo_user():
    """Test demo user authentication"""
    # Test user role
    user = authenticate_user("user", "user123")
    assert user is not None
    assert user["username"] == "user"
    assert user["role"] == "user"

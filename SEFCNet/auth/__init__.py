"""
Authentication Module for SEFCNet
===============================

This module provides comprehensive security and authentication features for the SEFCNet platform.
"""

from .auth_service import (
    AuthService,
    UserCreate,
    UserLogin,
    PasswordReset
)
from .routes import router as auth_router
from .security import (
    Role,
    Permission,
    User,
    Token,
    TokenData,
    SecurityConfig,
    get_current_user,
    check_permission,
    rate_limiter
)

__all__ = [
    'AuthService',
    'UserCreate',
    'UserLogin',
    'PasswordReset',
    'auth_router',
    'Role',
    'Permission',
    'User',
    'Token',
    'TokenData',
    'SecurityConfig',
    'get_current_user',
    'check_permission',
    'rate_limiter'
]
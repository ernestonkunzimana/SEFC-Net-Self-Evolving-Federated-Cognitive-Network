"""
Authentication API Routes for SEFCNet
===================================

This module provides RESTful API endpoints for:
- User registration and management
- Authentication and token handling
- Password reset functionality
- API key management
"""

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth_service import (
    AuthService, UserCreate, UserLogin, PasswordReset,
    User, Token, Role, Permission
)
from .security import get_current_user, check_permission, TokenData, rate_limiter

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    return await AuthService.register_user(user_data)

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """Authenticate user and return tokens."""
    return await AuthService.authenticate_user(login_data)

@router.post("/refresh", response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Get new access token using refresh token."""
    if not rate_limiter.is_allowed(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    return await AuthService.refresh_token(credentials.credentials)

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Logout user and invalidate refresh token."""
    await AuthService.logout(credentials.credentials)
    return {"detail": "Successfully logged out"}

@router.post("/password-reset-token")
async def create_password_reset_token(email: str):
    """Request password reset token."""
    reset_token = await AuthService.create_password_reset_token(email)
    # In production, send this token via email
    return {"reset_token": reset_token}

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """Reset password using reset token."""
    await AuthService.reset_password(reset_data)
    return {"detail": "Password successfully reset"}

@router.post("/api-key")
async def create_api_key(
    token_data: TokenData = Depends(get_current_user)
):
    """Create new API key for current user."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    api_key = await AuthService.create_api_key(token_data.user_id)
    return {"api_key": api_key}

@router.delete("/api-key/{api_key}")
async def revoke_api_key(
    api_key: str,
    token_data: TokenData = Depends(get_current_user)
):
    """Revoke an API key."""
    if not check_permission([Permission.MANAGE], token_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    await AuthService.revoke_api_key(token_data.user_id, api_key)
    return {"detail": "API key successfully revoked"}

@router.put("/roles")
async def update_roles(
    roles: list[Role],
    token_data: TokenData = Depends(get_current_user)
):
    """Update user roles."""
    if not Role.ADMIN in token_data.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update roles"
        )
    return await AuthService.update_user_roles(token_data.user_id, roles)

@router.put("/permissions")
async def update_permissions(
    permissions: list[Permission],
    token_data: TokenData = Depends(get_current_user)
):
    """Update user permissions."""
    if not Role.ADMIN in token_data.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update permissions"
        )
    return await AuthService.update_user_permissions(token_data.user_id, permissions)
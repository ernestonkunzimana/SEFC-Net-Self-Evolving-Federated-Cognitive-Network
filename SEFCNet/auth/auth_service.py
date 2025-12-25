"""
Authentication Service for SEFCNet
================================

This module provides authentication services including:
- User registration and management
- Login and token generation
- Password reset functionality
- API key management
- Session handling
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException, status

# Pydantic email type is optional – tests should still run without email_validator
try:  # pragma: no cover
    from pydantic import BaseModel, EmailStr as _RealEmailStr

    try:
        import email_validator  # type: ignore  # noqa: F401

        EmailStr = _RealEmailStr
    except Exception:
    #   email_validator is missing – degrade to plain string type
        EmailStr = str  # type: ignore
except Exception:  # pragma: no cover
    from pydantic import BaseModel

    EmailStr = str  # type: ignore

from .security import (
    User,
    Token,
    SecurityConfig,
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_api_key,
    encrypt_sensitive_data,
    decrypt_sensitive_data,
    Role,
    Permission,
)

try:  # jwt is used only in refresh_token path
    import jwt  # type: ignore
except Exception:  # pragma: no cover
    jwt = None  # type: ignore

# Database-backed storage
from .database import get_db

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    roles: List[Role]
    permissions: List[Permission]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordReset(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str

class AuthService:
    @staticmethod
    async def register_user(user_data: UserCreate) -> User:
        """Register a new user."""
        db = await get_db()
        
        # Check if email already exists
        existing = await db.get_user_by_email(user_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        import uuid
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            roles=user_data.roles,
            permissions=user_data.permissions,
            is_active=True,
            api_keys=[]
        )
        
        await db.create_user({
            'id': user.id,
            'email': user.email,
            'hashed_password': user.hashed_password,
            'roles': [r.value if hasattr(r, 'value') else str(r) for r in user.roles],
            'permissions': [p.value if hasattr(p, 'value') else str(p) for p in user.permissions],
            'is_active': user.is_active
        })
        
        # Return user with API keys
        user.api_keys = await db.get_api_keys(user.id)
        return user

    @staticmethod
    async def authenticate_user(login_data: UserLogin) -> Token:
        """Authenticate user and return tokens."""
        db = await get_db()
        user_data = await db.get_user_by_email(login_data.email)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not verify_password(login_data.password, user_data['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user_data.get('is_active', True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is inactive"
            )

        # Convert roles and permissions back to enums
        from .security import Role, Permission
        roles = [Role(r) if isinstance(r, str) else r for r in user_data.get('roles', [])]
        permissions = [Permission(p) if isinstance(p, str) else p for p in user_data.get('permissions', [])]

        # Create tokens
        access_token = create_access_token(
            data={
                "sub": user_data['id'],
                "roles": [r.value if hasattr(r, 'value') else str(r) for r in roles],
                "permissions": [p.value if hasattr(p, 'value') else str(p) for p in permissions]
            }
        )
        refresh_token = create_refresh_token(user_data['id'])

        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    @staticmethod
    async def refresh_token(refresh_token: str) -> Token:
        """Generate new access token using refresh token."""
        db = await get_db()
        
        if await db.is_token_blacklisted(refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been blacklisted"
            )

        try:
            payload = jwt.decode(
                refresh_token,
                SecurityConfig.SECRET_KEY,
                algorithms=[SecurityConfig.ALGORITHM]
            )
            user_id = payload["sub"]
            user_data = await db.get_user_by_id(user_id)
            
            if not user_data or not user_data.get('is_active', True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )

            # Convert roles and permissions
            from .security import Role, Permission
            roles = [Role(r) if isinstance(r, str) else r for r in user_data.get('roles', [])]
            permissions = [Permission(p) if isinstance(p, str) else p for p in user_data.get('permissions', [])]

            # Create new tokens
            access_token = create_access_token(
                data={
                    "sub": user_data['id'],
                    "roles": [r.value if hasattr(r, 'value') else str(r) for r in roles],
                    "permissions": [p.value if hasattr(p, 'value') else str(p) for p in permissions]
                }
            )
            new_refresh_token = create_refresh_token(user_data['id'])

            # Blacklist old refresh token
            await db.blacklist_token(refresh_token, user_id)

            return Token(
                access_token=access_token,
                refresh_token=new_refresh_token
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate refresh token"
            )

    @staticmethod
    async def logout(refresh_token: str) -> None:
        """Logout user by blacklisting their refresh token."""
        db = await get_db()
        # Try to extract user_id from token
        user_id = None
        try:
            if jwt:
                payload = jwt.decode(
                    refresh_token,
                    SecurityConfig.SECRET_KEY,
                    algorithms=[SecurityConfig.ALGORITHM]
                )
                user_id = payload.get("sub")
        except Exception:
            pass
        await db.blacklist_token(refresh_token, user_id)

    @staticmethod
    async def create_password_reset_token(email: EmailStr) -> str:
        """Create a password reset token."""
        db = await get_db()
        user_data = await db.get_user_by_email(email)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Use generic API-key generator as reset token source
        reset_token = create_api_key(user_data['id'], key_name="password_reset")
        expire = datetime.utcnow() + timedelta(
            minutes=SecurityConfig.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        )
        await db.create_reset_token(user_data['id'], reset_token, expire)
        
        return reset_token

    @staticmethod
    async def reset_password(reset_data: PasswordReset) -> None:
        """Reset user password using reset token."""
        db = await get_db()
        token_data = await db.get_reset_token(reset_data.reset_token)
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

        user_id, expire = token_data
        if datetime.utcnow() > expire:
            await db.delete_reset_token(reset_data.reset_token)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )

        user_data = await db.get_user_by_id(user_id)
        if not user_data or user_data['email'] != reset_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

        # Update password
        await db.update_user(user_id, {
            'hashed_password': get_password_hash(reset_data.new_password)
        })
        # Remove used reset token
        await db.delete_reset_token(reset_data.reset_token)
    
    @staticmethod
    async def get_user(user_id: str) -> Optional[User]:
        """Get user by ID."""
        db = await get_db()
        user_data = await db.get_user_by_id(user_id)
        if not user_data:
            return None
        
        # Get API keys
        api_keys = await db.get_api_keys(user_id)
        user_data['api_keys'] = api_keys
        
        # Convert roles and permissions back to enums
        from .security import Role, Permission
        roles = [Role(r) if isinstance(r, str) else r for r in user_data.get('roles', [])]
        permissions = [Permission(p) if isinstance(p, str) else p for p in user_data.get('permissions', [])]
        
        return User(
            id=user_data['id'],
            email=user_data['email'],
            hashed_password=user_data['hashed_password'],
            roles=roles,
            permissions=permissions,
            is_active=user_data.get('is_active', True),
            api_keys=api_keys
        )

    @staticmethod
    async def create_api_key(user_id: str) -> str:
        """Create a new API key for a user."""
        db = await get_db()
        user_data = await db.get_user_by_id(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        api_key = create_api_key(user_id)
        await db.add_api_key(user_id, api_key)
        return api_key

    @staticmethod
    async def revoke_api_key(user_id: str, api_key: str) -> None:
        """Revoke an API key."""
        db = await get_db()
        user_data = await db.get_user_by_id(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        api_keys = await db.get_api_keys(user_id)
        if api_key not in api_keys:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        await db.revoke_api_key(user_id, api_key)

    @staticmethod
    async def update_user_roles(
        user_id: str,
        roles: List[Role]
    ) -> User:
        """Update user roles."""
        db = await get_db()
        user_data = await db.get_user_by_id(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        await db.update_user(user_id, {
            'roles': [r.value if hasattr(r, 'value') else str(r) for r in roles]
        })
        
        updated_user = await db.get_user_by_id(user_id)
        # Get API keys
        api_keys = await db.get_api_keys(user_id)
        updated_user['api_keys'] = api_keys
        # Convert roles and permissions back to enums
        from .security import Role, Permission
        roles = [Role(r) if isinstance(r, str) else r for r in updated_user.get('roles', [])]
        permissions = [Permission(p) if isinstance(p, str) else p for p in updated_user.get('permissions', [])]
        return User(
            id=updated_user['id'],
            email=updated_user['email'],
            hashed_password=updated_user['hashed_password'],
            roles=roles,
            permissions=permissions,
            is_active=updated_user.get('is_active', True),
            api_keys=api_keys
        )

    @staticmethod
    async def update_user_permissions(
        user_id: str,
        permissions: List[Permission]
    ) -> User:
        """Update user permissions."""
        db = await get_db()
        user_data = await db.get_user_by_id(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        await db.update_user(user_id, {
            'permissions': [p.value if hasattr(p, 'value') else str(p) for p in permissions]
        })
        
        updated_user = await db.get_user_by_id(user_id)
        # Get API keys
        api_keys = await db.get_api_keys(user_id)
        updated_user['api_keys'] = api_keys
        # Convert roles and permissions back to enums
        from .security import Role, Permission
        roles = [Role(r) if isinstance(r, str) else r for r in updated_user.get('roles', [])]
        permissions = [Permission(p) if isinstance(p, str) else p for p in updated_user.get('permissions', [])]
        return User(
            id=updated_user['id'],
            email=updated_user['email'],
            hashed_password=updated_user['hashed_password'],
            roles=roles,
            permissions=permissions,
            is_active=updated_user.get('is_active', True),
            api_keys=api_keys
        )
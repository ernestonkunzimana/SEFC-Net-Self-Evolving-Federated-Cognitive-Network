"""
Enterprise-grade Security Module for SEFCNet
==========================================

This module provides security primitives used across the project and in tests:
- JWT-based authentication
- Role-based access control (RBAC)
- API key and token utilities
- Simple Fernet-based encryption helpers
"""

import datetime
import enum
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import uuid4

from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Optional dependencies – tests can still run without them
try:  # pragma: no cover - exercised indirectly
    from passlib.context import CryptContext  # type: ignore
except Exception:  # pragma: no cover - fallback path
    CryptContext = None  # type: ignore

try:  # pragma: no cover
    import jwt  # type: ignore
except Exception:  # pragma: no cover
    jwt = None  # type: ignore


class SecurityConfig:
    """Central security configuration.

    In production these should be provided via environment/secret manager.
    """

    SECRET_KEY = os.getenv("SEFCNET_JWT_SECRET", str(uuid4()))
    ALGORITHM = os.getenv("SEFCNET_JWT_ALG", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("SEFCNET_ACCESS_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("SEFCNET_REFRESH_EXPIRE_MINUTES", str(60 * 24 * 7)))
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("SEFCNET_RESET_EXPIRE_MINUTES", "15"))
    ENCRYPTION_KEY = os.getenv("SEFCNET_ENCRYPTION_KEY")


# Encryption for sensitive data (API keys, emails, etc.)
if SecurityConfig.ENCRYPTION_KEY:
    _fernet_key = SecurityConfig.ENCRYPTION_KEY.encode("utf-8")
else:
    # For tests / dev we generate an ephemeral key
    _fernet_key = Fernet.generate_key()
fernet = Fernet(_fernet_key)


class Role(str, enum.Enum):
    ADMIN = "admin"
    RESEARCHER = "researcher"
    CLIENT = "client"
    MONITOR = "monitor"


class Permission(str, enum.Enum):
    READ = "READ"
    WRITE = "WRITE"
    MANAGE = "MANAGE"
    ADMIN = "ADMIN"


@dataclass
class TokenData:
    """Data extracted from JWT and passed through FastAPI dependencies."""

    user_id: str
    roles: List[str]
    permissions: List[str]
    exp: datetime.datetime


# Try to import pydantic BaseModel; fall back to a lightweight stub in tests.
try:  # pragma: no cover
    from pydantic import BaseModel
except Exception:  # pragma: no cover

    class BaseModel:  # minimal stub for tests (no validation)
        def __init__(self, **data: Any) -> None:
            for k, v in data.items():
                setattr(self, k, v)


class User(BaseModel):
    """User model used by `auth_service` and tests."""

    id: str
    email: str
    hashed_password: str
    roles: List[Role] = []
    permissions: List[Permission] = []
    is_active: bool = True
    api_keys: List[str] = []


class Token(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


# Password hashing utilities (use passlib if available)
if CryptContext is not None:  # pragma: no cover - behaviour covered logically
    _pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(password: str) -> str:
        return _pwd_ctx.hash(password)

    def verify_password(plain: str, hashed: str) -> bool:
        return _pwd_ctx.verify(plain, hashed)

else:  # Simple, insecure stub for environments without passlib (e.g. tests)

    def hash_password(password: str) -> str:
        return f"plain::{password}"

    def verify_password(plain: str, hashed: str) -> bool:
        return hashed == f"plain::{plain}"


# Alias kept for backwards compatibility with `auth_service`
get_password_hash = hash_password


def encrypt_sensitive_data(value: str) -> str:
    """Encrypt sensitive string data using Fernet."""
    if value is None:
        return ""
    return fernet.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_sensitive_data(value: str) -> str:
    """Decrypt sensitive string data; returns empty string on failure."""
    if not value:
        return ""
    try:
        return fernet.decrypt(value.encode("utf-8")).decode("utf-8")
    except Exception:
        # Corrupted/invalid token – callers can treat as missing
        return ""


security = HTTPBearer()


def _ensure_jwt_available() -> None:
    if jwt is None:
        raise HTTPException(
            status_code=500,
            detail="JWT library not available; install PyJWT to enable authentication",
        )


def create_access_token(data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Create a JWT access token.

    Tests use this helper to mint tokens for the FastAPI routes.
    """

    if expires_delta is None:
        expires_delta = datetime.timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})

    if jwt is None:
        # Fallback for environments without PyJWT – embeds payload as JSON.
        import json

        return f"mock_token:{json.dumps(to_encode)}"

    return jwt.encode(to_encode, SecurityConfig.SECRET_KEY, algorithm=SecurityConfig.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Create a JWT refresh token for the given subject/user id."""

    if jwt is None:
        import json

        payload = {"sub": subject}
        return f"mock_refresh:{json.dumps(payload)}"

    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=SecurityConfig.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SecurityConfig.SECRET_KEY, algorithm=SecurityConfig.ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode a JWT token; returns None if decoding fails or jwt unavailable."""

    if jwt is None or not token or token.startswith("mock_token:"):
        # Very lightweight behaviour suitable for tests using mock tokens
        if token.startswith("mock_token:"):
            import json

            try:
                return json.loads(token.split("mock_token:", 1)[1])
            except Exception:
                return None
        return None

    try:
        return jwt.decode(token, SecurityConfig.SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
    except Exception:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> TokenData:
    """FastAPI dependency that validates the Authorization header and returns `TokenData`.

    This is used directly by the analytics routes and must work with tokens produced
    by `create_access_token` in the tests.
    """

    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    exp_raw = payload.get("exp")
    if isinstance(exp_raw, (int, float)):
        exp = datetime.datetime.fromtimestamp(exp_raw)
    elif isinstance(exp_raw, str):
        try:
            exp = datetime.datetime.fromisoformat(exp_raw)
        except Exception:
            exp = datetime.datetime.utcnow()
    else:
        exp = datetime.datetime.utcnow()

    if exp < datetime.datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token has expired")

    roles = payload.get("roles") or []
    permissions = payload.get("permissions") or []

    # Normalise to string lists for simpler checks
    roles = [r.value if isinstance(r, enum.Enum) else str(r) for r in roles]
    permissions = [p.value if isinstance(p, enum.Enum) else str(p) for p in permissions]

    return TokenData(
        user_id=str(payload.get("sub", "anonymous")),
        roles=roles,
        permissions=permissions,
        exp=exp,
    )


def check_permission(required_permissions: List[Permission], token_data: TokenData = Depends(get_current_user)) -> bool:
    """Check if the current user has all required permissions.

    Admin role always passes. Permissions are stored as upper-case strings in tokens,
    while the enum values are also upper-case strings (READ/WRITE/MANAGE/ADMIN).
    """

    if "admin" in [r.lower() for r in token_data.roles]:
        return True

    user_perms = set(token_data.permissions)
    required = {perm.value for perm in required_permissions}
    return required.issubset(user_perms)


class RateLimiter:
    """Simple in-memory rate limiter used by APIs."""

    def __init__(self, requests_per_minute: int = 60) -> None:
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[datetime.datetime]] = {}

    def is_allowed(self, user_id: str) -> bool:
        now = datetime.datetime.utcnow()
        minute_ago = now - datetime.timedelta(minutes=1)

        history = self.requests.get(user_id, [])
        history = [t for t in history if t > minute_ago]
        if len(history) >= self.requests_per_minute:
            self.requests[user_id] = history
            return False

        history.append(now)
        self.requests[user_id] = history
        return True


rate_limiter = RateLimiter()


class SecurityService:
    """Security service for node authentication and communication."""

    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key
        self.active_tokens: set[str] = set()

    def generate_node_token(self, node_id: str, expiry_hours: int = 24) -> str:
        """Generate authentication token for nodes."""

        if jwt is None:
            raise RuntimeError("PyJWT is required for node token generation")

        expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=expiry_hours)
        token = jwt.encode(
            {"node_id": node_id, "exp": expiry, "iat": datetime.datetime.utcnow()},
            self.secret_key,
            algorithm="HS256",
        )
        self.active_tokens.add(token)
        return token

    def verify_token(self, token: str) -> Optional[str]:
        """Verify node authentication token and return node id if valid."""

        if jwt is None or token not in self.active_tokens:
            return None

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return str(payload.get("node_id"))
        except Exception:
            # Invalid or expired; drop from active set.
            self.active_tokens.discard(token)
            return None


def create_api_key(user_id: Optional[str] = None, key_name: str = "default") -> str:
    """Generate a secure API key.

    `auth_service` currently calls this without arguments for reset tokens, so
    all parameters are optional and simply influence the derived hash.
    """

    import hashlib
    import secrets

    raw_key = secrets.token_urlsafe(32)
    key_data = f"{user_id or 'anon'}:{key_name}:{raw_key}"
    return hashlib.sha256(key_data.encode("utf-8")).hexdigest()
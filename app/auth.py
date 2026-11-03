"""
app/auth.py — Authentication, PBKDF2 password hashing, and HS256 JWT tokens.

Pure standard library implementation with zero external dependencies.
"""

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db

_bearer = HTTPBearer(auto_error=False)

_PBKDF2_ITERATIONS = 600_000
_SALT_LENGTH = 32


def hash_password(password: str) -> str:
    """Return a base64 encoded salt + derived PBKDF2-SHA256 key."""
    salt = os.urandom(_SALT_LENGTH)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _PBKDF2_ITERATIONS,
    )
    return base64.b64encode(salt + dk).decode("ascii")


def verify_password(password: str, hashed: str) -> bool:
    """Constant-time verification of password against PBKDF2-SHA256 hash."""
    try:
        data = base64.b64decode(hashed.encode("ascii"))
        salt = data[:_SALT_LENGTH]
        stored_dk = data[_SALT_LENGTH:]
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            _PBKDF2_ITERATIONS,
        )
        return hmac.compare_digest(dk, stored_dk)
    except Exception:
        return False


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(text: str) -> bytes:
    padding = 4 - len(text) % 4
    if padding != 4:
        text += "=" * padding
    return base64.urlsafe_b64decode(text.encode("ascii"))


def create_access_token(payload: dict) -> str:
    """Create signed HS256 JWT with expiration."""
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    claims = {
        **payload,
        "iat": now,
        "exp": now + settings.access_token_expire_minutes * 60,
    }

    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    claims_b64 = _b64url_encode(json.dumps(claims, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{header_b64}.{claims_b64}"
    raw_sig = hmac.new(
        settings.secret_key.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return f"{signing_input}.{_b64url_encode(raw_sig)}"


def decode_access_token(token: str) -> dict:
    """Verify and decode JWT token."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token structure")

    header_b64, claims_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{claims_b64}"

    expected_raw = hmac.new(
        settings.secret_key.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    expected_b64 = _b64url_encode(expected_raw)

    if not hmac.compare_digest(sig_b64, expected_b64):
        raise ValueError("Token signature is invalid")

    claims = json.loads(_b64url_decode(claims_b64))

    if claims.get("exp", 0) < time.time():
        raise ValueError("Token has expired")

    return claims


class CurrentUser:
    """Identity container for authenticated user."""
    __slots__ = ("id", "email", "role", "full_name", "awareness_score")

    def __init__(self, id: int, email: str, role: str, full_name: str, awareness_score: int):
        self.id = id
        self.email = email
        self.role = role
        self.full_name = full_name
        self.awareness_score = awareness_score

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_analyst(self) -> bool:
        return self.role in ("analyst", "admin")


def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(_bearer)] = None,
    db: Session = Depends(get_db),
) -> CurrentUser:
    """FastAPI dependency for mandatory authenticated endpoints."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from app.models.db_models import UserDB

    user = db.query(UserDB).filter(UserDB.id == claims.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(
        id=user.id,
        email=user.email,
        role=user.role,
        full_name=user.full_name,
        awareness_score=user.awareness_score,
    )


def get_optional_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(_bearer)] = None,
    db: Session = Depends(get_db),
) -> Optional[CurrentUser]:
    """FastAPI dependency for endpoints that work both for guests and signed-in users."""
    if credentials is None:
        return None

    try:
        claims = decode_access_token(credentials.credentials)
        from app.models.db_models import UserDB

        user = db.query(UserDB).filter(UserDB.id == claims.get("sub")).first()
        if user and user.is_active:
            return CurrentUser(
                id=user.id,
                email=user.email,
                role=user.role,
                full_name=user.full_name,
                awareness_score=user.awareness_score,
            )
    except Exception:
        pass
    return None


def require_admin(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    """Enforces admin role."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required.",
        )
    return current_user


def require_analyst(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    """Enforces analyst or admin role."""
    if not current_user.is_analyst:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Fact-check analyst or administrator privileges required.",
        )
    return current_user

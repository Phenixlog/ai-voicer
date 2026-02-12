"""Authentication service for Théoria SaaS."""
import os
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

import jwt
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import get_db, get_db_context
from .models import User, RefreshToken

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer(auto_error=False)


def create_access_token(user_id: str) -> str:
    """Create short-lived JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str, device_info: Optional[str] = None) -> Tuple[str, str]:
    """Create refresh token and return (token_id, token)."""
    token_id = str(uuid.uuid4())
    token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    with get_db_context() as db:
        refresh = RefreshToken(
            id=token_id,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expire,
            device_info=device_info,
        )
        db.add(refresh)
        db.commit()
    
    return token_id, token


def verify_access_token(token: str) -> Optional[str]:
    """Verify JWT and return user_id if valid."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_refresh_token(token: str) -> Optional[str]:
    """Verify refresh token and return user_id if valid."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    with get_db_context() as db:
        refresh = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not refresh:
            return None
        
        return refresh.user_id


def revoke_refresh_token(token: str) -> bool:
    """Revoke a refresh token."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    with get_db_context() as db:
        refresh = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None)
        ).first()
        
        if refresh:
            refresh.revoked_at = datetime.utcnow()
            db.commit()
            return True
    return False


def revoke_all_user_tokens(user_id: str) -> int:
    """Revoke all refresh tokens for a user."""
    with get_db_context() as db:
        tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None)
        ).all()
        
        count = 0
        now = datetime.utcnow()
        for token in tokens:
            token.revoked_at = now
            count += 1
        
        db.commit()
        return count


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """FastAPI dependency to get current authenticated user."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    user_id = verify_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        if user.status != "active":
            raise HTTPException(status_code=403, detail="Account suspended")
        
        return user
    finally:
        db.close()


async def get_current_user_or_none(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[str]:
    """Optional auth - returns user_id or None."""
    if not credentials:
        return None
    return verify_access_token(credentials.credentials)

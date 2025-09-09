from passlib.context import CryptContext
from schemas.user_schemas import UserPublic
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from jwt.exceptions import InvalidTokenError
import jwt
from uuid import UUID
from models.models import User, RefreshToken
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from settings import get_settings
from dependencies import SessionDep
import secrets

"""
authentication_service.py

Handles all authentication-related logic, including:
- Password hashing and verification
- JWT access token creation and validation
- Refresh token issuance, verification, rotation, and revocation
- Current user dependencies for FastAPI routes


This module integrates with:
- SQLAlchemy ORM models (User, RefreshToken)
- FastAPI security utilities (OAuth2PasswordBearer)
- Pydantic models for token schemas

It ensures that both access tokens (short-lived) and refresh tokens (long-lived) 
are securely managed for client authentication.
"""

#Load settings defined in .env
jwt_settings = get_settings()
SECRET_KEY = jwt_settings.jwt_secret_key
ALGORITHM = jwt_settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = jwt_settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = jwt_settings.refresh_token_expire_days

class Token(BaseModel):
    """Token schema used for returning access_token and refresh_token in API responses."""
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str


# Setup oauth2 schema and bcrypt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", refreshUrl="auth/refresh")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(session: SessionDep, username: str) -> User | None:
    """Get a User | None object based on username """
    stmt = select(User).where(User.username == username)
    user = session.execute(stmt).scalar_one_or_none()
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Creates a JWT token based on data dict, sets expires date and issued at"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    issued_at = datetime.now(timezone.utc)
    to_encode.update({"exp": expire})
    to_encode.update({"iat": issued_at})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: UUID, device_name: str, session: SessionDep) -> RefreshToken:
    """Creates a refresh_token, based on device_name and user_id and stores in database"""
    
    # Generates a URL safe base64 encoded string
    token = secrets.token_urlsafe(32)

    # Set timestamp for when the refresh_token should expire
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    # Check if token already exist for user+device
    stmt = select(RefreshToken).where((RefreshToken.user_id == user_id) & (RefreshToken.device_name == device_name))
    db_token = session.execute(stmt).scalar_one_or_none()

    if db_token: # rotate token for user+device combination
        db_token.token = token
        db_token.expires_at = expires_at
        db_token.revoked = False
    else: # create a new row for user+device in database
        db_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            device_name=device_name
        )
        session.add(db_token)

    # commit changes to database
    session.commit()
    session.refresh(db_token)
    return db_token

def verify_refresh_token(refresh_token: str, session: SessionDep) -> RefreshToken:
    """Validate refresh_token and return the corresponding RefreshToken object if valid."""
    stsm = select(RefreshToken).where(RefreshToken.token == refresh_token)
    db_token = session.execute(stsm).scalar_one_or_none()
    
    # checks if token exist, is revoked or expired.
    if not db_token or db_token.revoked or db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    
    return db_token

def revoke_refresh_token(refresh_token: str, session: SessionDep) -> None:
    """Revokes a given refresh_token"""
    stmt = select(RefreshToken).where(RefreshToken.token == refresh_token)
    db_token = session.execute(stmt).scalar_one_or_none()
    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    # sets the user+device to be revoked
    db_token.revoked = True
    session.commit()


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep) -> User:
    """Get current user using the Oauth2 scheme (Authorization Header)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Get user_id from payload
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception
    
    # Get user based on user_id received from jwt payload
    user = session.get(User, UUID(token_data.user_id))
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[UserPublic, Depends(get_current_user)]) -> UserPublic:
    """Get current user from get_current_user and checks if the user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
    return current_user

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain_password is equal to hashed_password"""
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, plain_password: str, session: SessionDep):
    """Checks if user exist in database and the plain_password matches stored password"""
    user = get_user(session, username)
    if not user:
        return False
    if not verify_password(plain_password, user.hashed_password):
        return False
    return user

CurrentUser = Annotated[User, Depends(get_current_active_user)]
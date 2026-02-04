"""
Authentication routes for signup, login, and user management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.db.session import get_db
from app.db.models import User
from app.core.security import create_access_token, get_current_user_id
from app.auth.utils import (
    hash_password,
    verify_password,
    validate_password_strength,
    validate_email,
    validate_username,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============== Pydantic Schemas ==============

class SignupRequest(BaseModel):
    """Request schema for user registration."""
    email: str
    username: str
    password: str


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """Response schema for user data."""
    id: int
    email: str
    username: str
    is_active: bool
    is_admin: bool
    created_at: str


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


# ============== Routes ==============

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Register a new user account.

    Args:
        request: Signup request with email, username, and password
        db: Database session

    Returns:
        JWT access token and user data

    Raises:
        HTTPException: If validation fails or user already exists
    """
    # Validate email
    is_valid, error = validate_email(request.email)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Validate username
    is_valid, error = validate_username(request.username)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Validate password strength
    is_valid, error = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == request.username.lower()).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is already taken"
        )

    # Create new user
    new_user = User(
        email=request.email.lower(),
        username=request.username.lower(),
        hashed_password=hash_password(request.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate access token
    access_token = create_access_token(data={"sub": str(new_user.id)})

    return TokenResponse(
        access_token=access_token,
        user={
            "id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
            "is_admin": new_user.is_admin,
        }
    )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Authenticate user and return access token.

    Args:
        request: Login request with email and password
        db: Database session

    Returns:
        JWT access token and user data

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email.lower()).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_admin": user.is_admin,
        }
    )


@router.get("/me", response_model=UserResponse)
def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get the currently authenticated user's profile.

    Args:
        user_id: Current user ID from JWT token
        db: Database session

    Returns:
        User profile data

    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at.isoformat()
    )


@router.post("/verify", response_model=MessageResponse)
def verify_token_endpoint(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Verify if the current token is valid.

    Args:
        user_id: Current user ID from JWT token
        db: Database session

    Returns:
        Success message if token is valid

    Raises:
        HTTPException: If token is invalid
    """
    # If we reach here, token is valid (dependency already validated it)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return MessageResponse(message="Token is valid")

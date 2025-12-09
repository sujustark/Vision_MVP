"""
Authentication API endpoints for user registration and login.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from ..db import get_db_session
from ..models import User, UserRole
from ..utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
import re

router = APIRouter()

# Request/Response Models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str  # "studio" or "customer"
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['studio', 'customer']:
            raise ValueError('Role must be either "studio" or "customer"')
        return v
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return v.strip()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    role: str
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    role: str
    is_active: bool

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db_session)):
    """
    Register a new user account.
    
    Args:
        request: Signup request with email, password, full_name, and role
        db: Database session
    
    Returns:
        User information and access token
    
    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(request.password)
    new_user = User(
        email=request.email,
        password_hash=hashed_password,
        full_name=request.full_name,
        role=UserRole(request.role),
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate access token
    access_token = create_access_token(data={"sub": new_user.id})
    
    return AuthResponse(
        user_id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role.value,
        access_token=access_token
    )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db_session)):
    """
    Authenticate a user and return an access token.
    
    Args:
        request: Login request with email and password
        db: Database session
    
    Returns:
        User information and access token
    
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.id})
    
    return AuthResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        access_token=access_token
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user from token
    
    Returns:
        User information
    """
    return UserResponse(
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        is_active=current_user.is_active
    )

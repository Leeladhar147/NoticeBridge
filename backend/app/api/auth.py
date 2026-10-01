from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import User
from app.services.auth_service import AuthService, get_current_user
from app.repositories.employee_repo import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: str
    email_verified: bool = False
    message: str


class UserProfileResponse(BaseModel):
    id: int
    name: str
    full_name: str
    email: str
    email_verified: bool = False


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Creates a new user account with hashed password and returns an authenticated JWT session."""
    clean_email = payload.email.strip().lower()
    
    if "@" not in clean_email or "." not in clean_email.split("@")[-1]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address format."
        )

    if len(payload.password.strip()) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )

    existing = UserRepository.get_by_email(db, clean_email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Secure bcrypt password hash
    password_hash = AuthService.hash_password(payload.password)
    user = UserRepository.create_user(
        db=db,
        name=payload.full_name,
        email=clean_email,
        password_hash=password_hash,
        email_verified=False
    )

    token = AuthService.create_access_token({"sub": str(user.id), "email": user.email})

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.name,
        email_verified=user.email_verified,
        message="Account created successfully."
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates user credentials and returns a secure JWT access token."""
    clean_email = payload.email.strip().lower()
    user = UserRepository.get_by_email(db, clean_email)
    
    if not user or not AuthService.verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = AuthService.create_access_token({"sub": str(user.id), "email": user.email})

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.name,
        email_verified=user.email_verified,
        message="Login successful."
    )


@router.post("/logout")
def logout():
    """Logs out the user session."""
    return {"message": "Logged out successfully."}


@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's profile."""
    return UserProfileResponse(
        id=current_user.id,
        name=current_user.name,
        full_name=current_user.name,
        email=current_user.email,
        email_verified=current_user.email_verified
    )


@router.post("/seed-demo")
def seed_demo(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Allows authenticated user to load demo sample records if desired for exploration."""
    UserRepository.seed_demo_profile_for_user(db, current_user)
    return {"message": "Demonstration scenario loaded for current user."}

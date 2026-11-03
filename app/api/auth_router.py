"""
app/api/auth_router.py — User registration, login, profile, and demo quick-sign-in.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import UserDB
from app.models.schemas import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
    ForgotPasswordRequest,
    ProfileUpdateRequest,
)
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    CurrentUser,
)
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user account with PBKDF2-SHA256 password security."""
    existing = db.query(UserDB).filter(UserDB.email == req.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address is already registered.",
        )

    # Validate Admin privilege secret
    assigned_role = "user"
    if req.role == "admin":
        if req.admin_secret != settings.admin_secret:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid admin registration secret key.",
            )
        assigned_role = "admin"
    elif req.role == "analyst":
        assigned_role = "analyst"

    new_user = UserDB(
        email=req.email.lower(),
        full_name=req.full_name.strip(),
        hashed_password=hash_password(req.password),
        role=assigned_role,
        awareness_score=0,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({
        "sub": new_user.id,
        "email": new_user.email,
        "role": new_user.role,
        "name": new_user.full_name,
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user),
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates user and returns JWT access token."""
    user = db.query(UserDB).filter(UserDB.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or deactivated.",
        )

    token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "name": user.full_name,
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns currently authenticated user profile."""
    user = db.query(UserDB).filter(UserDB.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.put("/profile", response_model=UserResponse)
def update_profile(
    req: ProfileUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates user profile information."""
    user = db.query(UserDB).filter(UserDB.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if req.full_name:
        user.full_name = req.full_name.strip()
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Simulated password reset recovery trigger."""
    user = db.query(UserDB).filter(UserDB.email == req.email.lower()).first()
    return {
        "message": f"If an account is associated with {req.email}, password reset instructions have been dispatched.",
        "success": True,
    }


@router.post("/demo-login/{role}", response_model=TokenResponse)
def demo_login(role: str, db: Session = Depends(get_db)):
    """1-Click quick login for reviewers and evaluation (admin, analyst, or user)."""
    email_map = {
        "admin": "admin@truthguard.ai",
        "analyst": "analyst@truthguard.ai",
        "user": "citizen@truthguard.ai",
    }
    target_email = email_map.get(role.lower(), "admin@truthguard.ai")
    user = db.query(UserDB).filter(UserDB.email == target_email).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Demo user for role '{role}' not found.")

    token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "name": user.full_name,
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )

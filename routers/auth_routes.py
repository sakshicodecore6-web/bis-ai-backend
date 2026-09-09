# routers/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models import User
from schemas import UserRegister, UserLogin, TokenResponse
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: UserRegister, session: Session = Depends(get_session)):
    # Check if a user with this email already exists
    existing_user = session.exec(
        select(User).where(User.email == payload.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    new_user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)  # loads the auto-generated id back onto new_user

    token = create_access_token(data={"sub": new_user.email})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == payload.email)).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    token = create_access_token(data={"sub": user.email})
    return TokenResponse(access_token=token)
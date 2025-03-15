import requests
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from services.auth import AuthService
from database.repositories import UserRepository
from database.connection import get_db
from database.models import User
from database.schemas import UserOut, UserCreate,UserAuth, Token

from settings import settings

from api.depends import get_current_user

router = APIRouter(prefix="/auth")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repository=user_repo, settings=settings)
    created_user = auth_service.register_user(user_in)
    if created_user is None:
        raise HTTPException(status_code=400, detail="User already exists")
    return created_user

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repository=user_repo, settings=settings)
    user_auth = UserAuth(email=form_data.username, password=form_data.password)
    auth_user = auth_service.authenticate_user(user_auth)
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(subject=str(auth_user.id))
    return {"access_token": access_token,
            "token_type": "bearer"
            }

@router.get("/profile", response_model=UserOut)
def get_profile(
        current_user: int = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    service = AuthService(user_repository=user_repo, settings=settings)
    user = service.user_by_id(int(current_user))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/profile/{user_id}", response_model=UserOut)
def get_profile_by_id(
        user_id: int,
        db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    service = AuthService(user_repository=user_repo, settings=settings)
    user = service.user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

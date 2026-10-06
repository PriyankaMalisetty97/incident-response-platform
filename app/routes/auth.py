from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserRead
from app.security import create_access_token
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if user_service.get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    try:
        return user_service.create_user(db, data)
    except IntegrityError:  # two requests registering the same email at the same moment
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # The OAuth2 form calls the field "username"; we use it for the email.
    user = user_service.authenticate(db, form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user

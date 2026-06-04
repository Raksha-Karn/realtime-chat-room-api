from app.auth import hash_password, verify_password, create_access_token, decode_token
from app.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from app.schema import UserOut, UserCreate, Token, UserSearchOut
from sqlalchemy.orm import Session
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(User).where((User.email == user.email) | (User.username == user.username))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already exists!")
    new_user = User(email=user.email, username=user.username, hashed_password=hash_password(user.password))
    db.add(new_user); db.commit(); db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token, status_code=200)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.email == form.username)).scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials!", headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def get_me(current_user=Depends(decode_token)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }

@router.get("/users/search", response_model=list[UserSearchOut])
def search_users(q: str, db: Session = Depends(get_db), current_user=Depends(decode_token)):
    term = q.strip()
    if len(term) < 2:
        return []
    pattern = f"%{term}%"
    return db.execute(
        select(User)
        .where(User.is_deleted == False)
        .where(User.username.ilike(pattern))
        .order_by(User.username.asc())
        .limit(20)
    ).scalars().all()

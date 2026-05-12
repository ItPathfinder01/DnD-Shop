from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, get_superadmin
from models import User
from schemas import AdminUserResponse, UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[AdminUserResponse])
def list_users(db: Session = Depends(get_db), _: User = Depends(get_superadmin)):
    return db.query(User).all()


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(get_superadmin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.post("/users/{user_id}/make-superadmin", response_model=UserResponse)
def make_superadmin(user_id: int, db: Session = Depends(get_db), _: User = Depends(get_superadmin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.is_superadmin = True
    db.commit()
    db.refresh(user)
    return user


@router.post("/init-superadmin")
def init_superadmin(email: str, db: Session = Depends(get_db)):
    """Одноразовый эндпоинт: делает первого пользователя суперадмином по email."""
    if db.query(User).filter(User.is_superadmin == True).count() > 0:
        raise HTTPException(status_code=400, detail="Суперадмин уже существует")
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.is_superadmin = True
    db.commit()
    return {"detail": f"{email} теперь суперадмин"}

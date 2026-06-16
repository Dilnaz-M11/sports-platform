from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session  # ← Изменено: вместо AsyncSession
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from models.database import get_db
from repositories.user_repository import UserRepository
from config import settings

router = APIRouter(prefix="/auth", tags=["Аутентификация"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class UserCreate(BaseModel):
    login: str = Field(..., description="Логин пользователя")
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., description="Пароль")
    birth_date: Optional[str] = Field(None, description="Дата рождения (ГГГГ-ММ-ДД)")
    weight_kg: Optional[float] = Field(None, description="Вес в килограммах")
    height_cm: Optional[float] = Field(None, description="Рост в сантиметрах")
    gender: Optional[str] = Field(None, description="Пол (male/female)")
    fitness_level: Optional[str] = Field(None, description="Уровень подготовки (beginner/intermediate/advanced)")
    rest_hr: Optional[int] = Field(None, description="Пульс покоя")
    max_hr: Optional[int] = Field(None, description="Максимальный пульс")

class UserResponse(BaseModel):
    id: int
    login: str
    email: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

def hash_password(password: str) -> str:
    """Хэширование пароля с помощью bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# ✅ ИСПРАВЛЕНО: убраны async/await, AsyncSession → Session
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except JWTError:
        raise credentials_exception
    except ValueError:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)  # ← убрали await
    if user is None:
        raise credentials_exception
    return user

# ✅ ИСПРАВЛЕНО: убраны async/await
@router.post("/register", summary="Регистрация пользователя")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    user_repo = UserRepository(db)
    
    # Проверка существования пользователя
    existing_user = user_repo.get_user_by_login(user_data.login)  # ← убрали await
    if existing_user:
        raise HTTPException(status_code=400, detail="Логин уже используется")
    
    existing_email = user_repo.get_user_by_email(user_data.email)  # ← убрали await
    if existing_email:
        raise HTTPException(status_code=400, detail="Email уже используется")
    
    # Хэширование пароля
    hashed = hash_password(user_data.password)
    user_dict = user_data.dict(exclude={"password"})
    user_dict["password_hash"] = hashed
    
    # Преобразование даты рождения
    if user_dict.get("birth_date"):
        user_dict["birth_date"] = datetime.strptime(user_dict["birth_date"], "%Y-%m-%d").date()
    
    # Создание пользователя
    new_user = user_repo.create_user(user_dict)  # ← убрали await
    
    return UserResponse(
        id=new_user.id, 
        login=new_user.login, 
        email=new_user.email, 
        created_at=new_user.created_at
    )

# ✅ ИСПРАВЛЕНО: убраны async/await
@router.post("/login", summary="Вход в систему")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Аутентификация пользователя и выдача токена"""
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_login(form_data.username)  # ← убрали await
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
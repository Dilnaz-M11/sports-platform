from sqlalchemy import Column, Integer, String, Date, Float, DateTime, Enum
from sqlalchemy.sql import func
from .database import Base
import enum

class GenderEnum(enum.Enum):
    male = "male"
    female = "female"

class FitnessLevelEnum(enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    weight_kg = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    fitness_level = Column(Enum(FitnessLevelEnum), default=FitnessLevelEnum.beginner)
    rest_hr = Column(Integer, nullable=True)
    max_hr = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
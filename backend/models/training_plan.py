from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from .database import Base

class TrainingPlan(Base):
    __tablename__ = "training_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    
    week_number = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    workout_type = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    distance_km = Column(Float, nullable=True)
    intensity_zone = Column(Integer, nullable=True)
    intensity_description = Column(String(100), nullable=True)
    
    # Новые поля для научных расчётов
    calories = Column(Integer, nullable=True)           # расход калорий за тренировку (по MET)
    trimp = Column(Float, nullable=True)                # тренировочный импульс (формула Банистера)
    target_hr_zone = Column(String(50), nullable=True)  # целевая пульсовая зона (например "132-147")
    predicted_weight = Column(Float, nullable=True)     # прогнозируемый вес после недели
    
    completed = Column(Integer, default=0)
    completed_date = Column(Date, nullable=True)
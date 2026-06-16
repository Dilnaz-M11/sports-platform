import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.sql import func
from .database import Base

class GoalTypeEnum(enum.Enum):
    WEIGHT_LOSS = "weight_loss"
    ENDURANCE = "endurance"
    STRENGTH = "strength"
    HEALTH = "health"

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_type = Column(String(50), nullable=False)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=True)
    deadline_weeks = Column(Integer, default=8)
    status = Column(String(20), default="active")
    created_at = Column(Date, server_default=func.current_date())
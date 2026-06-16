from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class Training(Base):
    __tablename__ = "trainings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    sport_type = Column(String(50), nullable=False)
    distance_meters = Column(Float, nullable=True)
    avg_hr = Column(Integer, nullable=True)
    max_hr = Column(Integer, nullable=True)
    perceived_effort = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
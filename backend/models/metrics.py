from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from .database import Base

class ActivityMetric(Base):
    __tablename__ = "activity_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    training_id = Column(Integer, ForeignKey("trainings.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String(50), nullable=False)
    metric_value = Column(Float, nullable=False)

class CumulativeMetric(Base):
    __tablename__ = "cumulative_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    ctl = Column(Float, nullable=True)
    atl = Column(Float, nullable=True)
    tsb = Column(Float, nullable=True)
    
    __table_args__ = (UniqueConstraint('user_id', 'date', name='unique_user_date'),)
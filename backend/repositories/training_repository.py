from sqlalchemy.orm import Session  # ← Изменено
from sqlalchemy import select, update, delete, and_
from datetime import datetime
from models.training import Training

class TrainingRepository:
    def __init__(self, session: Session):  # ← Изменено
        self.session = session
    
    def add_training(self, training_data: dict) -> Training:  # ← убрали async
        training = Training(**training_data)
        self.session.add(training)
        self.session.commit()
        self.session.refresh(training)
        return training
    
    def get_trainings_by_user(self, user_id: int, limit: int = 100, offset: int = 0):  # ← убрали async
        result = self.session.execute(
            select(Training)
            .where(Training.user_id == user_id)
            .order_by(Training.start_time.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    def get_trainings_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime):  # ← убрали async
        result = self.session.execute(
            select(Training)
            .where(
                and_(
                    Training.user_id == user_id,
                    Training.start_time >= start_date,
                    Training.start_time <= end_date
                )
            )
            .order_by(Training.start_time)
        )
        return result.scalars().all()
    
    def get_training_by_id(self, training_id: int, user_id: int) -> Training | None:  # ← убрали async
        result = self.session.execute(
            select(Training).where(
                and_(Training.id == training_id, Training.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()
    
    def update_training(self, training_id: int, user_id: int, update_data: dict) -> Training | None:  # ← убрали async
        self.session.execute(
            update(Training)
            .where(and_(Training.id == training_id, Training.user_id == user_id))
            .values(**update_data)
        )
        self.session.commit()
        return self.get_training_by_id(training_id, user_id)
    
    def delete_training(self, training_id: int, user_id: int) -> bool:  # ← убрали async
        result = self.session.execute(
            delete(Training).where(and_(Training.id == training_id, Training.user_id == user_id))
        )
        self.session.commit()
        return result.rowcount > 0
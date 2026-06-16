from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from datetime import datetime
from models.training import Training

class TrainingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_training(self, training_data: dict) -> Training:
        training = Training(**training_data)
        self.session.add(training)
        await self.session.commit()
        await self.session.refresh(training)
        return training
    
    async def get_trainings_by_user(self, user_id: int, limit: int = 100, offset: int = 0):
        result = await self.session.execute(
            select(Training)
            .where(Training.user_id == user_id)
            .order_by(Training.start_time.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_trainings_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime):
        result = await self.session.execute(
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
    
    async def get_training_by_id(self, training_id: int, user_id: int) -> Training | None:
        result = await self.session.execute(
            select(Training).where(
                and_(Training.id == training_id, Training.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()
    
    async def update_training(self, training_id: int, user_id: int, update_data: dict) -> Training | None:
        await self.session.execute(
            update(Training)
            .where(and_(Training.id == training_id, Training.user_id == user_id))
            .values(**update_data)
        )
        await self.session.commit()
        return await self.get_training_by_id(training_id, user_id)
    
    async def delete_training(self, training_id: int, user_id: int) -> bool:
        result = await self.session.execute(
            delete(Training).where(and_(Training.id == training_id, Training.user_id == user_id))
        )
        await self.session.commit()
        return result.rowcount > 0
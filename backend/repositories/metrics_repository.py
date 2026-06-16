from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import date
from models.metrics import ActivityMetric, CumulativeMetric

class MetricsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_metric(self, training_id: int, metric_type: str, metric_value: float) -> ActivityMetric:
        metric = ActivityMetric(training_id=training_id, metric_type=metric_type, metric_value=metric_value)
        self.session.add(metric)
        await self.session.commit()
        return metric
    
    async def get_metrics_by_training(self, training_id: int):
        result = await self.session.execute(
            select(ActivityMetric).where(ActivityMetric.training_id == training_id)
        )
        return result.scalars().all()
    
    async def add_cumulative_metric(self, user_id: int, metric_date: date, ctl: float, atl: float, tsb: float):
        await self.session.execute(
            delete(CumulativeMetric).where(
                CumulativeMetric.user_id == user_id,
                CumulativeMetric.date == metric_date
            )
        )
        
        cumulative = CumulativeMetric(user_id=user_id, date=metric_date, ctl=ctl, atl=atl, tsb=tsb)
        self.session.add(cumulative)
        await self.session.commit()
        return cumulative
    
    async def get_cumulative_metrics_by_user(self, user_id: int, start_date: date, end_date: date):
        result = await self.session.execute(
            select(CumulativeMetric)
            .where(
                CumulativeMetric.user_id == user_id,
                CumulativeMetric.date >= start_date,
                CumulativeMetric.date <= end_date
            )
            .order_by(CumulativeMetric.date)
        )
        return result.scalars().all()
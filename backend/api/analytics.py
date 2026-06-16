from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from models.database import get_db
from repositories.training_repository import TrainingRepository
from repositories.metrics_repository import MetricsRepository
from services.analytics_service import AnalyticsService
from api.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/analytics", tags=["Аналитика"])

@router.get("/dashboard", summary="Получить дашборд аналитики")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Используем UTC с часовым поясом
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=60)
    
    training_repo = TrainingRepository(db)
    trainings = await training_repo.get_trainings_by_date_range(
        current_user.id, start_date, end_date
    )
    
    # Получение TRIMP для каждой тренировки
    metrics_repo = MetricsRepository(db)
    daily_trimp = defaultdict(float)
    
    for t in trainings:
        metrics = await metrics_repo.get_metrics_by_training(t.id)
        for m in metrics:
            if m.metric_type == "TRIMP":
                daily_trimp[t.start_time.date()] += m.metric_value
                break
    
    # Расчет кумулятивных показателей
    ctl_atl_tsb = AnalyticsService.calculate_ctl_atl_tsb(dict(daily_trimp))
    
    # Текущий TSB
    current_tsb = None
    if ctl_atl_tsb:
        last_date = max(ctl_atl_tsb.keys())
        current_tsb = ctl_atl_tsb[last_date]['tsb']
    
    # Состояние спортсмена
    state_info = None
    if current_tsb is not None:
        state_info = AnalyticsService.get_state_by_tsb(current_tsb)
    
    # Последние 5 тренировок
    recent = trainings[-5:] if len(trainings) > 5 else trainings
    recent_list = []
    for t in reversed(recent):
        recent_list.append({
            "id": t.id,
            "date": t.start_time.strftime("%d.%m.%Y"),
            "sport_type": t.sport_type,
            "duration_min": round(t.duration_seconds / 60, 0),
            "distance_km": round(t.distance_meters / 1000, 1) if t.distance_meters else None
        })
    
    # Статистика за неделю
    week_ago = end_date - timedelta(days=7)
    week_trainings = [t for t in trainings if t.start_time >= week_ago]
    week_stats = {
        "total_trainings": len(week_trainings),
        "total_duration_min": sum(t.duration_seconds for t in week_trainings) // 60,
        "total_distance_km": round(sum(t.distance_meters or 0 for t in week_trainings) / 1000, 1)
    }
    
    # Дни без тренировок
    if trainings:
        last_training_date = max(t.start_time for t in trainings)
        days_without = (datetime.now(timezone.utc).date() - last_training_date.date()).days
    else:
        days_without = 999
    
    # Рекомендации
    recommendations = AnalyticsService.generate_recommendations(
        tsb=current_tsb or 0,
        days_without_training=days_without
    )
    
    # Перевод состояний на русский
    if state_info:
        state_translation = {
            "peak_form": "Пик формы",
            "good_form": "Хорошая форма",
            "fatigue": "Накопленное утомление",
            "high_fatigue": "Высокое утомление",
            "overtraining": "Перетренированность"
        }
        state_info["message_ru"] = state_translation.get(state_info["state"], state_info["message"])
    
    return {
        "tsb": current_tsb,
        "state": state_info,
        "recent_trainings": recent_list,
        "week_stats": week_stats,
        "recommendations": recommendations,
        "ctl_atl_tsb_data": [
            {"date": d.isoformat(), "ctl": v['ctl'], "atl": v['atl'], "tsb": v['tsb']}
            for d, v in ctl_atl_tsb.items()
        ]
    }

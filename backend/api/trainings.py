from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from models.database import get_db
from repositories.training_repository import TrainingRepository
from repositories.metrics_repository import MetricsRepository
from services.analytics_service import AnalyticsService
from api.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/trainings", tags=["Тренировки"])

class TrainingCreate(BaseModel):
    start_time: str = Field(..., description="Дата и время начала (ГГГГ-ММ-ДДTЧЧ:ММ:СС)")
    duration_seconds: int = Field(..., description="Продолжительность в секундах")
    sport_type: str = Field(..., description="Вид спорта (бег, велоспорт, плавание, силовая, другое)")
    distance_meters: Optional[float] = Field(None, description="Дистанция в метрах")
    avg_hr: Optional[int] = Field(None, description="Средний пульс")
    max_hr: Optional[int] = Field(None, description="Максимальный пульс")
    perceived_effort: Optional[int] = Field(None, description="Оценка усилий (1-10)")
    notes: Optional[str] = Field(None, description="Заметки")

@router.post("/add", summary="Добавить тренировку")
async def add_training(
    training_data: TrainingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        print(f"DEBUG: Получены данные: {training_data}")
        print(f"DEBUG: Пользователь ID: {current_user.id}")
        
        start_time = datetime.fromisoformat(training_data.start_time)
        
        training_dict = training_data.dict()
        training_dict["user_id"] = current_user.id
        training_dict["start_time"] = start_time
        
        print(f"DEBUG: Словарь для сохранения: {training_dict}")
        
        training_repo = TrainingRepository(db)
        new_training = await training_repo.add_training(training_dict)
        
        print(f"DEBUG: Тренировка создана с ID: {new_training.id}")
        
        # Расчёт TRIMP (если есть данные о пульсе)
        if training_data.avg_hr and training_data.max_hr:
            try:
                age = None
                if current_user.birth_date:
                    age = datetime.now().year - current_user.birth_date.year
                
                max_hr = current_user.max_hr or (220 - age) if age else 220
                rest_hr = current_user.rest_hr or (70 if current_user.gender == "male" else 75)
                
                trimp = AnalyticsService.calculate_trimp(
                    duration_minutes=training_data.duration_seconds / 60,
                    avg_hr=training_data.avg_hr,
                    max_hr=max_hr,
                    rest_hr=rest_hr,
                    gender=current_user.gender or "male"
                )
                
                if trimp:
                    metrics_repo = MetricsRepository(db)
                    await metrics_repo.add_metric(new_training.id, "TRIMP", trimp)
                    print(f"DEBUG: TRIMP рассчитан: {trimp}")
            except Exception as e:
                print(f"DEBUG: Ошибка расчёта TRIMP: {e}")
        
        return {"message": "Тренировка добавлена", "training_id": new_training.id}
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", summary="Список тренировок")
async def get_trainings(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        training_repo = TrainingRepository(db)
        trainings = await training_repo.get_trainings_by_user(current_user.id, limit, offset)
        
        result = []
        for t in trainings:
            result.append({
                "id": t.id,
                "start_time": t.start_time.isoformat(),
                "duration_seconds": t.duration_seconds,
                "sport_type": t.sport_type,
                "distance_meters": t.distance_meters,
                "avg_hr": t.avg_hr,
                "max_hr": t.max_hr
            })
        
        return {"trainings": result, "count": len(result)}
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{training_id}", summary="Детали тренировки")
async def get_training(
    training_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        training_repo = TrainingRepository(db)
        training = await training_repo.get_training_by_id(training_id, current_user.id)
        
        if not training:
            raise HTTPException(status_code=404, detail="Тренировка не найдена")
        
        metrics_repo = MetricsRepository(db)
        metrics = await metrics_repo.get_metrics_by_training(training_id)
        
        metrics_dict = {m.metric_type: m.metric_value for m in metrics}
        
        return {
            "id": training.id,
            "start_time": training.start_time.isoformat(),
            "duration_seconds": training.duration_seconds,
            "sport_type": training.sport_type,
            "distance_meters": training.distance_meters,
            "avg_hr": training.avg_hr,
            "max_hr": training.max_hr,
            "perceived_effort": training.perceived_effort,
            "notes": training.notes,
            "trimp": metrics_dict.get("TRIMP")
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{training_id}", summary="Удалить тренировку")
async def delete_training(
    training_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        training_repo = TrainingRepository(db)
        success = await training_repo.delete_training(training_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Тренировка не найдена")
        
        return {"message": "Тренировка удалена"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from pydantic import BaseModel
from typing import Optional
from datetime import date

from models.database import get_db
from models.user import User, GenderEnum, FitnessLevelEnum
from models.goal import Goal
from models.training_plan import TrainingPlan
from services.plan_service import PlanService
from api.auth import get_current_user

router = APIRouter(prefix="/plan", tags=["План тренировок"])

# Модели Pydantic для валидации данных
class UserDataUpdate(BaseModel):
    birth_date: date
    gender: str
    weight_kg: float
    height_cm: float
    fitness_level: str
    rest_hr: Optional[int] = None
    max_hr: Optional[int] = None

class GoalCreate(BaseModel):
    goal_type: str
    target_value: float
    deadline_weeks: Optional[int] = 8


@router.post("/update-profile")
async def update_user_profile(
    user_data: UserDataUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновление антропометрических данных пользователя"""
    current_user.birth_date = user_data.birth_date
    current_user.gender = GenderEnum(user_data.gender)
    current_user.weight_kg = user_data.weight_kg
    current_user.height_cm = user_data.height_cm
    current_user.fitness_level = FitnessLevelEnum(user_data.fitness_level)
    current_user.rest_hr = user_data.rest_hr
    current_user.max_hr = user_data.max_hr
    
    await db.commit()
    await db.refresh(current_user)
    
    return {"message": "Профиль обновлён", "user_id": current_user.id}


@router.post("/create-goal")
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создание цели пользователя"""
    # Архивируем старые активные цели
    await db.execute(
        update(Goal).where(Goal.user_id == current_user.id, Goal.status == "active").values(status="archived")
    )
    
    goal = Goal(
        user_id=current_user.id,
        goal_type=goal_data.goal_type,
        target_value=goal_data.target_value,
        deadline_weeks=goal_data.deadline_weeks
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    
    return {"message": "Цель создана", "goal_id": goal.id}


@router.post("/generate")
async def generate_training_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Генерация тренировочного плана на основе последней активной цели"""
    # Получаем последнюю активную цель
    result = await db.execute(
        select(Goal).where(
            Goal.user_id == current_user.id,
            Goal.status == "active"
        ).order_by(Goal.id.desc())
    )
    goal = result.scalar_one_or_none()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена. Сначала создайте цель.")
    
    # Удаляем старый план
    await db.execute(delete(TrainingPlan).where(TrainingPlan.user_id == current_user.id))
    
    # Генерируем новый план
    weeks = goal.deadline_weeks or 8
    plan_data = PlanService.generate_plan(current_user, goal, weeks)
    
    # Сохраняем план в БД
    for item in plan_data:
        training = TrainingPlan(
            user_id=current_user.id,
            goal_id=goal.id,
            week_number=item["week"],
            day_of_week=item["day"],
            workout_type=item["workout_type"],
            duration_minutes=item["duration_min"],
            distance_km=item.get("distance_km"),
            intensity_zone=item["intensity_zone"],
            intensity_description=item["intensity_desc"],
            # Новые поля для научных расчётов
            calories=item.get("calories"),
            trimp=item.get("trimp"),
            target_hr_zone=item.get("target_hr_zone"),
            predicted_weight=item.get("predicted_weight")
        )
        db.add(training)
    
    await db.commit()
    
    return {
        "message": "План сгенерирован",
        "weeks": weeks,
        "total_trainings": len(plan_data),
        "plan": plan_data
    }


@router.get("/current")
async def get_current_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение текущего тренировочного плана"""
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.user_id == current_user.id
        ).order_by(TrainingPlan.week_number, TrainingPlan.day_of_week)
    )
    plan = result.scalars().all()
    
    # Группируем по неделям
    weeks_data = {}
    for item in plan:
        if item.week_number not in weeks_data:
            weeks_data[item.week_number] = []
        weeks_data[item.week_number].append({
            "id": item.id,
            "day": item.day_of_week,
            "workout_type": item.workout_type,
            "duration_min": item.duration_minutes,
            "distance_km": item.distance_km,
            "intensity_zone": item.intensity_zone,
            "intensity_desc": item.intensity_description,
            "calories": item.calories,
            "trimp": item.trimp,
            "target_hr_zone": item.target_hr_zone,
            "predicted_weight": item.predicted_weight,
            "completed": item.completed
        })
    
    return {
        "total_weeks": len(weeks_data),
        "weeks": weeks_data
    }


@router.post("/complete/{plan_id}")
async def complete_training(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Отметить тренировку как выполненную"""
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.id == plan_id,
            TrainingPlan.user_id == current_user.id
        )
    )
    training = result.scalar_one_or_none()
    
    if not training:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")
    
    training.completed = 1
    training.completed_date = date.today()
    await db.commit()
    
    return {"message": "Тренировка отмечена как выполненная"}
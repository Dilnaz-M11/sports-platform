from datetime import date
from typing import List, Dict
import math

class PlanService:
    
    @staticmethod
    def calculate_age(birth_date: date) -> int:
        """Расчёт возраста на основе даты рождения"""
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    @staticmethod
    def calculate_bmr(user) -> float:
        """
        Базовый уровень метаболизма (BMR)
        Формула Миффлина-Сан-Жеора
        """
        age = PlanService.calculate_age(user.birth_date)
        weight = user.weight_kg
        height = user.height_cm
        gender = user.gender.value if hasattr(user.gender, 'value') else user.gender
        
        if gender == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        return round(bmr, 0)
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str = "moderate") -> float:
        """
        Общий суточный расход калорий (TDEE)
        Коэффициенты активности:
        - sedentary: 1.2 (сидячий образ жизни)
        - light: 1.375 (лёгкая активность)
        - moderate: 1.55 (умеренная активность)
        - active: 1.725 (высокая активность)
        - very_active: 1.9 (очень высокая)
        """
        coefficients = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        coef = coefficients.get(activity_level, 1.55)
        return round(bmr * coef, 0)
    
    @staticmethod
    def calculate_max_hr(user) -> int:
        """
        Максимальная частота сердечных сокращений
        Формула Танака: 208 - 0.7 × возраст
        """
        if user.max_hr:
            return user.max_hr
        age = PlanService.calculate_age(user.birth_date)
        return int(208 - 0.7 * age)
    
    @staticmethod
    def calculate_hr_zones(user) -> Dict[int, Dict]:
        """
        Пульсовые зоны по методу Карвонена
        """
        max_hr = PlanService.calculate_max_hr(user)
        rest_hr = user.rest_hr if user.rest_hr else (70 if user.gender.value == "male" else 75)
        
        hrr = max_hr - rest_hr  # пульсовой резерв
        
        zones = {
            1: {"min": rest_hr + 0.5 * hrr, "max": rest_hr + 0.6 * hrr, "name": "Восстановительная", "effect": "Активное восстановление"},
            2: {"min": rest_hr + 0.6 * hrr, "max": rest_hr + 0.7 * hrr, "name": "Жиросжигающая", "effect": "Оптимальное окисление жиров"},
            3: {"min": rest_hr + 0.7 * hrr, "max": rest_hr + 0.8 * hrr, "name": "Аэробная", "effect": "Повышение выносливости"},
            4: {"min": rest_hr + 0.8 * hrr, "max": rest_hr + 0.9 * hrr, "name": "Анаэробная", "effect": "Развитие скоростной выносливости"},
            5: {"min": rest_hr + 0.9 * hrr, "max": max_hr, "name": "Максимальная", "effect": "Развитие максимальной мощности"}
        }
        
        return zones
    
    @staticmethod
    def calculate_trimp(duration_min: float, avg_hr: int, user) -> float:
        """
        Тренировочный импульс (TRIMP)
        Формула Банистера: TRIMP = время × отношение_пульса × e^(k × отношение_пульса)
        """
        if avg_hr is None:
            return None
        
        max_hr = PlanService.calculate_max_hr(user)
        rest_hr = user.rest_hr if user.rest_hr else (70 if user.gender.value == "male" else 75)
        
        # Отношение пульса
        hr_ratio = (avg_hr - rest_hr) / (max_hr - rest_hr)
        hr_ratio = max(0, min(hr_ratio, 1))  # ограничиваем от 0 до 1
        
        # Коэффициент k зависит от пола
        gender = user.gender.value if hasattr(user.gender, 'value') else user.gender
        k = 1.92 if gender == "male" else 1.67
        
        # TRIMP
        trimp = duration_min * hr_ratio * math.exp(k * hr_ratio)
        
        return round(trimp, 1)
    
    @staticmethod
    def calculate_weekly_calorie_deficit(user, goal, weeks: int) -> Dict:
        """
        Расчёт недельного дефицита калорий для снижения веса
        """
        current_weight = user.weight_kg
        target_weight = goal.target_value
        total_loss = current_weight - target_weight
        
        if total_loss <= 0:
            return {"deficit_per_day": 0, "loss_per_week": 0, "recommended_calories": None}
        
        # Для снижения 1 кг нужно сжечь ~7700 ккал
        total_calorie_deficit = total_loss * 7700
        deficit_per_week = total_calorie_deficit / weeks
        deficit_per_day = deficit_per_week / 7
        
        # Ограничиваем безопасный дефицит (не более 500 ккал в день)
        if deficit_per_day > 500:
            deficit_per_day = 500
            weeks = total_calorie_deficit / (deficit_per_day * 7)
        
        # Расчёт рекомендуемой калорийности
        bmr = PlanService.calculate_bmr(user)
        tdee = PlanService.calculate_tdee(bmr, "moderate")
        recommended_calories = tdee - deficit_per_day
        
        return {
            "deficit_per_day": round(deficit_per_day, 0),
            "loss_per_week": round((deficit_per_day * 7) / 7700, 1),
            "recommended_calories": round(recommended_calories, 0),
            "weeks_needed": round(weeks, 1)
        }
    
    @staticmethod
    def generate_plan_for_weight_loss(user, goal, weeks: int = 8) -> List[Dict]:
        """Генерация плана для снижения веса (с научными расчётами)"""
        plan = []
        current_weight = user.weight_kg
        target_weight = goal.target_value
        
        # Расчёт дефицита калорий
        calorie_plan = PlanService.calculate_weekly_calorie_deficit(user, goal, weeks)
        
        # Пульсовые зоны
        hr_zones = PlanService.calculate_hr_zones(user)
        
        # Множитель интенсивности в зависимости от уровня подготовки
        intensity_multiplier = {"beginner": 0.6, "intermediate": 0.8, "advanced": 1.0}
        level = user.fitness_level.value if hasattr(user.fitness_level, 'value') else user.fitness_level
        multiplier = intensity_multiplier.get(level, 0.7)
        
        # Список активностей с MET (метаболический эквивалент)
        activities = [
            {"type": "бег (8 км/ч)", "met": 8, "icon": "🏃", "hr_zone": 3},
            {"type": "велоспорт (20 км/ч)", "met": 6, "icon": "🚲", "hr_zone": 2},
            {"type": "плавание (умеренно)", "met": 7, "icon": "🏊", "hr_zone": 2},
            {"type": "скакалка", "met": 10, "icon": "🪢", "hr_zone": 4},
            {"type": "HIIT (интервалы)", "met": 11, "icon": "⚡", "hr_zone": 4},
            {"type": "эллипс", "met": 6, "icon": "🏃‍♂️", "hr_zone": 2},
            {"type": "гребля", "met": 7, "icon": "🚣", "hr_zone": 3},
            {"type": "кроссфит", "met": 9, "icon": "💪", "hr_zone": 4},
        ]
        
        for week in range(1, weeks + 1):
            week_intensity = min(multiplier * (1 + 0.08 * (week - 1)), 1.2)
            training_days = [2, 4, 6] if week < 4 else [1, 3, 5, 6]
            
            for day in training_days:
                duration = min(20 + (week - 1) * 3, 50)
                
                # Выбираем активность
                if day in [1, 3, 5]:
                    # Высокоинтенсивные
                    intense_activities = [act for act in activities if act["met"] > 8]
                    activity = intense_activities[(week + day) % len(intense_activities)]
                    intensity_zone = 4 if week > 3 else 3
                    intensity_desc = "высокая" if week > 3 else "средняя"
                else:
                    # Аэробные
                    aerobic_activities = [act for act in activities if act["met"] <= 7]
                    activity = aerobic_activities[(week * day) % len(aerobic_activities)]
                    intensity_zone = 2 if week < 4 else 3
                    intensity_desc = "средняя" if week < 4 else "умеренно-высокая"
                
                # Расчёт калорий по MET
                calories_per_min = activity["met"] * 3.5 * user.weight_kg / 200
                calories = round(calories_per_min * duration * week_intensity)
                
                # Расчёт TRIMP (теоретический)
                target_hr_zone = hr_zones.get(intensity_zone, hr_zones[3])
                avg_hr = round((target_hr_zone["min"] + target_hr_zone["max"]) / 2)
                trimp = PlanService.calculate_trimp(duration, avg_hr, user)
                
                # Расчёт дистанции
                distance = None
                if "бег" in activity["type"]:
                    speed = 8 if intensity_zone >= 3 else 6
                    distance = round((duration / 60) * speed * week_intensity, 1)
                elif "велоспорт" in activity["type"]:
                    speed = 20 if intensity_zone >= 3 else 15
                    distance = round((duration / 60) * speed * week_intensity, 1)
                elif "плавание" in activity["type"]:
                    speed = 2.5
                    distance = round((duration / 60) * speed * week_intensity, 1)
                
                # Прогнозируемый вес
                predicted_weight = round(current_weight - calorie_plan["loss_per_week"] * week, 1)
                
                plan.append({
                    "week": week,
                    "day": day,
                    "workout_type": f"{activity['icon']} {activity['type']}",
                    "duration_min": duration,
                    "distance_km": distance,
                    "calories": calories,
                    "trimp": trimp,
                    "target_hr_zone": f"{target_hr_zone['min']:.0f}-{target_hr_zone['max']:.0f}",
                    "predicted_weight": predicted_weight,
                    "intensity_zone": intensity_zone,
                    "intensity_desc": intensity_desc
                })
        
        return plan
    
    @staticmethod
    def generate_plan_for_endurance(user, goal, weeks: int = 8) -> List[Dict]:
        """Генерация плана для улучшения выносливости (бег с расчётами)"""
        plan = []
        target_distance_km = goal.target_value
        
        # Пульсовые зоны
        hr_zones = PlanService.calculate_hr_zones(user)
        
        level_map = {"beginner": 2, "intermediate": 5, "advanced": 8}
        level = user.fitness_level.value if hasattr(user.fitness_level, 'value') else user.fitness_level
        current_distance_km = level_map.get(level, 3)
        
        weekly_increase = (target_distance_km - current_distance_km) / weeks if target_distance_km > current_distance_km else 0.5
        
        for week in range(1, weeks + 1):
            weekly_distance = min(current_distance_km + weekly_increase * week, target_distance_km * 1.1)
            runs_per_week = 3 if week < 4 else 4
            days = [2, 4, 6] if runs_per_week == 3 else [1, 3, 5, 6]
            
            for day in days:
                if day == 6:
                    distance = weekly_distance * 0.45
                    intensity_zone = 2
                    intensity_desc = "лёгкая"
                elif day in [2, 4]:
                    distance = weekly_distance * 0.3
                    intensity_zone = 3
                    intensity_desc = "средняя"
                else:
                    distance = weekly_distance * 0.25
                    intensity_zone = 4 if week > 3 else 3
                    intensity_desc = "высокая" if week > 3 else "средняя"
                
                duration = int(distance / 8 * 60)
                
                # Расчёт TRIMP
                target_hr_zone = hr_zones.get(intensity_zone, hr_zones[3])
                avg_hr = round((target_hr_zone["min"] + target_hr_zone["max"]) / 2)
                trimp = PlanService.calculate_trimp(duration, avg_hr, user)
                
                plan.append({
                    "week": week,
                    "day": day,
                    "workout_type": "🏃 бег",
                    "duration_min": duration,
                    "distance_km": round(distance, 1),
                    "trimp": trimp,
                    "target_hr_zone": f"{target_hr_zone['min']:.0f}-{target_hr_zone['max']:.0f}",
                    "intensity_zone": intensity_zone,
                    "intensity_desc": intensity_desc
                })
        return plan
    
    @staticmethod
    def generate_plan_for_health(user, weeks: int = 6) -> List[Dict]:
        """Генерация плана для общего оздоровления"""
        plan = []
        
        # Уровень подготовки пользователя
        level_map = {
            "beginner": (15, 3),   # (длительность в минутах, частота в неделю)
            "intermediate": (20, 4),
            "advanced": (25, 5)
        }
        level = user.fitness_level.value if hasattr(user.fitness_level, 'value') else user.fitness_level
        base_duration, base_frequency = level_map.get(level, (15, 3))
        
        # Пульсовые зоны
        hr_zones = PlanService.calculate_hr_zones(user)
        
        # ✅ ИСПРАВЛЕНО: список упражнений с иконками
        exercises = [
            {"name": "Растяжка всего тела", "icon": "🧘", "hr_zone": 1, "calories_per_min": 3},
            {"name": "Наклоны и скручивания", "icon": "🔄", "hr_zone": 2, "calories_per_min": 4},
            {"name": "Упражнения для спины", "icon": "💪", "hr_zone": 2, "calories_per_min": 4},
            {"name": "Укрепление пресса", "icon": "🏋️", "hr_zone": 3, "calories_per_min": 5},
            {"name": "Комплекс на равновесие", "icon": "⚖️", "hr_zone": 2, "calories_per_min": 3},
            {"name": "Дыхательная гимнастика", "icon": "🌬️", "hr_zone": 1, "calories_per_min": 2},
            {"name": "Суставная гимнастика", "icon": "🦵", "hr_zone": 1, "calories_per_min": 3},
            {"name": "Кардио (лёгкое)", "icon": "❤️", "hr_zone": 2, "calories_per_min": 6},
        ]
        
        for week in range(1, weeks + 1):
            # Увеличиваем длительность каждую неделю
            duration = min(base_duration + (week - 1) * 2, 40)
            frequency = base_frequency
            
            # Определяем дни тренировок
            if frequency == 3:
                days = [2, 4, 6]  # Вт, Чт, Сб
            elif frequency == 4:
                days = [1, 3, 5, 6]  # Пн, Ср, Пт, Сб
            else:
                days = [1, 2, 3, 5, 6]  # Пн, Вт, Ср, Пт, Сб
            
            for i, day in enumerate(days):
                # Выбираем упражнение
                exercise_idx = (week + i) % len(exercises)
                exercise = exercises[exercise_idx]
                
                # Интенсивность зависит от недели
                if week < 3:
                    intensity_desc = "лёгкая"
                    intensity_zone = exercise["hr_zone"]
                else:
                    intensity_desc = "средняя"
                    intensity_zone = min(exercise["hr_zone"] + 1, 4)
                
                # Расчёт калорий
                calories = round(duration * exercise["calories_per_min"])
                
                # Расчёт TRIMP
                target_hr_zone = hr_zones.get(intensity_zone, hr_zones[2])
                avg_hr = round((target_hr_zone["min"] + target_hr_zone["max"]) / 2)
                trimp = PlanService.calculate_trimp(duration, avg_hr, user)
                
                # ✅ ИСПРАВЛЕНО: все переменные определены
                plan.append({
                    "week": week,
                    "day": day,
                    "workout_type": f"{exercise['icon']} {exercise['name']}",
                    "duration_min": duration,
                    "distance_km": None,  # Для здоровья дистанция не учитывается
                    "calories": calories,
                    "trimp": trimp,
                    "target_hr_zone": f"{target_hr_zone['min']:.0f}-{target_hr_zone['max']:.0f}",
                    "predicted_weight": None,  # Для здоровья прогноз веса не нужен
                    "intensity_zone": intensity_zone,
                    "intensity_desc": intensity_desc
                })
        
        return plan
    
    @staticmethod
    def generate_plan(user, goal, weeks: int = 8) -> List[Dict]:
        """Главная функция генерации плана в зависимости от типа цели"""
        if goal.goal_type == "weight_loss":
            return PlanService.generate_plan_for_weight_loss(user, goal, weeks)
        elif goal.goal_type == "endurance":
            return PlanService.generate_plan_for_endurance(user, goal, weeks)
        elif goal.goal_type == "health":
            return PlanService.generate_plan_for_health(user, weeks)
        else:
            return PlanService.generate_plan_for_health(user, weeks)
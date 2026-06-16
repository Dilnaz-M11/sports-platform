from math import exp
from datetime import date
from typing import Dict, List, Any

class AnalyticsService:
    
    @staticmethod
    def calculate_trimp(duration_minutes: float, avg_hr: float, max_hr: float, 
                        rest_hr: float = 70, gender: str = "male") -> float:
        """Расчет тренировочного импульса (TRIMP)"""
        if max_hr is None or avg_hr is None:
            return None
        
        hr_ratio = (avg_hr - rest_hr) / (max_hr - rest_hr)
        k = 1.92 if gender == "male" else 1.67
        trimp = duration_minutes * hr_ratio * exp(k * hr_ratio)
        return round(trimp, 2)
    
    @staticmethod
    def calculate_ctl_atl_tsb(trainings_by_day: Dict[date, float]) -> Dict[date, Dict[str, float]]:
        """Расчет кумулятивных показателей: CTL, ATL, TSB"""
        if not trainings_by_day:
            return {}
        
        tau_ctl = 42
        tau_atl = 7
        alpha_ctl = 2 / (tau_ctl + 1)
        alpha_atl = 2 / (tau_atl + 1)
        
        sorted_dates = sorted(trainings_by_day.keys())
        
        results = {}
        ctl = 0
        atl = 0
        
        for dt in sorted_dates:
            trimp_today = trainings_by_day.get(dt, 0)
            ctl = ctl + alpha_ctl * (trimp_today - ctl)
            atl = atl + alpha_atl * (trimp_today - atl)
            tsb = ctl - atl
            
            results[dt] = {
                'ctl': round(ctl, 2),
                'atl': round(atl, 2),
                'tsb': round(tsb, 2)
            }
        
        return results
    
    @staticmethod
    def get_state_by_tsb(tsb: float) -> Dict[str, Any]:
        """Определение состояния спортсмена на основе TSB"""
        if tsb > 10:
            return {"state": "peak_form", "message": "Пик формы", "color": "green", "recommendation": "Благоприятно для соревнований"}
        elif 0 < tsb <= 10:
            return {"state": "good_form", "message": "Хорошая форма", "color": "lightgreen", "recommendation": "Поддерживайте текущий уровень"}
        elif -10 < tsb <= 0:
            return {"state": "fatigue", "message": "Накопленное утомление", "color": "yellow", "recommendation": "Контролируйте восстановление"}
        elif -20 < tsb <= -10:
            return {"state": "high_fatigue", "message": "Высокое утомление", "color": "orange", "recommendation": "Риск перетренированности, снизьте нагрузку"}
        else:
            return {"state": "overtraining", "message": "Перетренированность", "color": "red", "recommendation": "Требуется отдых"}
    
    @staticmethod
    def generate_recommendations(tsb: float, days_without_training: int, 
                                   vo2max_progress: float = None) -> List[str]:
        """Генерация рекомендаций на основе анализа"""
        recommendations = []
        
        if tsb < -15:
            recommendations.append("⚠️ Ваш уровень утомления высок. Рекомендуется снизить интенсивность тренировок и увеличить время на восстановление.")
        elif tsb > 10:
            recommendations.append("✅ Ваша форма достигла пика. Это отличное время для соревнований или установления личных рекордов.")
        
        if days_without_training > 5:
            recommendations.append(f"📝 Вы не тренировались последние {days_without_training} дней. Постепенное возвращение к нагрузкам поможет избежать травм.")
        
        if vo2max_progress is not None:
            if vo2max_progress > 3:
                recommendations.append("📈 Ваша аэробная форма улучшается. Продолжайте в том же духе!")
            elif vo2max_progress < -3:
                recommendations.append("⚠️ Ваша аэробная форма снижается. Рекомендуется добавить больше кардионагрузок.")
        
        if not recommendations:
            recommendations.append("👍 Все показатели в норме. Продолжайте тренироваться в текущем режиме!")
        
        return recommendations
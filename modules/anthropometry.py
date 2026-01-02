"""
Anthropometry and metabolism calculation module
Mifflin-St Jeor equation for BMR calculation
"""
from config import config


def calculate_bmr(gender: str, weight: float, height: float, age: int) -> float:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor equation
    
    Args:
        gender: 'male' or 'female'
        weight: weight in kg
        height: height in cm
        age: age in years
    
    Returns:
        BMR in kcal/day
    """
    base = 10 * weight + 6.25 * height - 5 * age
    
    if gender == "male":
        return base + 5
    else:  # female
        return base - 161


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure
    
    Args:
        bmr: Basal Metabolic Rate
        activity_level: one of: minimal, low, medium, high, extreme
    
    Returns:
        TDEE in kcal/day
    """
    coefficient = config.ACTIVITY_LEVELS.get(activity_level, 1.2)
    return bmr * coefficient


def calculate_target_calories(tdee: float, goal: str) -> float:
    """
    Calculate target daily calories based on goal
    
    Args:
        tdee: Total Daily Energy Expenditure
        goal: 'lose', 'maintain', or 'gain'
    
    Returns:
        Target calories in kcal/day
    """
    adjustment = config.GOALS.get(goal, 0)
    return tdee + adjustment


def calculate_macros(target_calories: float, goal: str) -> dict:
    """
    Calculate macronutrients distribution
    
    Args:
        target_calories: target daily calories
        goal: 'lose', 'maintain', or 'gain'
    
    Returns:
        Dict with protein, fat, carbs in grams
    """
    ratios = config.MACROS.get(goal, config.MACROS["maintain"])
    
    # Calories per gram: protein=4, fat=9, carbs=4
    protein_kcal = target_calories * ratios["protein"]
    fat_kcal = target_calories * ratios["fat"]
    carbs_kcal = target_calories * ratios["carbs"]
    
    return {
        "protein": round(protein_kcal / 4),  # grams
        "fat": round(fat_kcal / 9),          # grams
        "carbs": round(carbs_kcal / 4)       # grams
    }


def calculate_all(gender: str, weight: float, height: float, age: int, 
                  activity_level: str, goal: str) -> dict:
    """
    Calculate all metabolic parameters
    
    Returns:
        Dict with bmr, tdee, target_calories, macros
    """
    bmr = calculate_bmr(gender, weight, height, age)
    tdee = calculate_tdee(bmr, activity_level)
    target_calories = calculate_target_calories(tdee, goal)
    macros = calculate_macros(target_calories, goal)
    
    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target_calories": round(target_calories),
        "protein": macros["protein"],
        "fat": macros["fat"],
        "carbs": macros["carbs"]
    }


def get_activity_level_description(level: str) -> str:
    """Get human-readable description of activity level"""
    descriptions = {
        "minimal": "🪑 Минимальная (сидячий образ жизни)",
        "low": "🚶 Низкая (1-3 тренировки в неделю)",
        "medium": "🏃 Средняя (3-5 тренировок в неделю)",
        "high": "💪 Высокая (6-7 тренировок в неделю)",
        "extreme": "🔥 Очень высокая (2 раза в день)"
    }
    return descriptions.get(level, level)


def get_goal_description(goal: str) -> str:
    """Get human-readable description of goal"""
    descriptions = {
        "lose": "📉 Похудение (снижение веса)",
        "maintain": "⚖️ Поддержание веса",
        "gain": "📈 Набор мышечной массы"
    }
    return descriptions.get(goal, goal)


def format_nutrition_summary(data: dict) -> str:
    """Format nutrition data as readable message"""
    return f"""
📊 *Ваши показатели:*

🔥 Базовый метаболизм (BMR): *{data['bmr']} ккал*
⚡ Суточный расход (TDEE): *{data['tdee']} ккал*
🎯 Целевой калораж: *{data['target_calories']} ккал*

📋 *Рекомендуемое БЖУ:*
🥩 Белки: *{data['protein']} г*
🧈 Жиры: *{data['fat']} г*
🍚 Углеводы: *{data['carbs']} г*
"""

"""
Training plan generator module
Generates personalized workout plans based on user goals and preferences
"""
import json
import random
from pathlib import Path
from typing import List, Dict, Optional


# Exercise database
EXERCISES = {
    "home": {
        "chest": [
            {"name": "Отжимания классические", "muscles": "грудные, трицепс", "sets": 3, "reps": "10-15"},
            {"name": "Отжимания с широкой постановкой рук", "muscles": "грудные", "sets": 3, "reps": "10-12"},
            {"name": "Отжимания с узкой постановкой рук", "muscles": "трицепс, грудные", "sets": 3, "reps": "8-12"},
            {"name": "Отжимания с ногами на возвышении", "muscles": "верх груди", "sets": 3, "reps": "8-10"},
        ],
        "back": [
            {"name": "Подтягивания (если есть турник)", "muscles": "широчайшие, бицепс", "sets": 3, "reps": "5-10"},
            {"name": "Горизонтальные подтягивания", "muscles": "спина, бицепс", "sets": 3, "reps": "10-12"},
            {"name": "Супермен (лодочка)", "muscles": "разгибатели спины", "sets": 3, "reps": "15-20"},
            {"name": "Тяга резинки к поясу", "muscles": "широчайшие", "sets": 3, "reps": "12-15"},
        ],
        "legs": [
            {"name": "Приседания", "muscles": "квадрицепс, ягодицы", "sets": 4, "reps": "15-20"},
            {"name": "Выпады на месте", "muscles": "квадрицепс, ягодицы", "sets": 3, "reps": "12 на ногу"},
            {"name": "Болгарские приседания", "muscles": "квадрицепс, ягодицы", "sets": 3, "reps": "10 на ногу"},
            {"name": "Ягодичный мостик", "muscles": "ягодицы, бицепс бедра", "sets": 3, "reps": "15-20"},
            {"name": "Подъёмы на носки", "muscles": "икры", "sets": 3, "reps": "20-25"},
        ],
        "shoulders": [
            {"name": "Отжимания уголком", "muscles": "дельты", "sets": 3, "reps": "8-12"},
            {"name": "Подъёмы рук в стороны с бутылками", "muscles": "средние дельты", "sets": 3, "reps": "12-15"},
            {"name": "Жим с пола с резинкой", "muscles": "дельты", "sets": 3, "reps": "12-15"},
        ],
        "arms": [
            {"name": "Сгибания рук с бутылками", "muscles": "бицепс", "sets": 3, "reps": "12-15"},
            {"name": "Обратные отжимания от опоры", "muscles": "трицепс", "sets": 3, "reps": "10-15"},
            {"name": "Планка на вытянутых руках", "muscles": "кор, руки", "sets": 3, "reps": "30-60 сек"},
        ],
        "core": [
            {"name": "Планка", "muscles": "кор", "sets": 3, "reps": "30-60 сек"},
            {"name": "Скручивания", "muscles": "пресс", "sets": 3, "reps": "15-20"},
            {"name": "Подъёмы ног лёжа", "muscles": "нижний пресс", "sets": 3, "reps": "12-15"},
            {"name": "Велосипед", "muscles": "косые мышцы", "sets": 3, "reps": "20 на сторону"},
            {"name": "Альпинист", "muscles": "кор, кардио", "sets": 3, "reps": "30 сек"},
        ],
        "cardio": [
            {"name": "Бёрпи", "muscles": "всё тело", "sets": 3, "reps": "10"},
            {"name": "Jumping Jacks", "muscles": "кардио", "sets": 3, "reps": "30 сек"},
            {"name": "Бег на месте с высоким подниманием колен", "muscles": "кардио, ноги", "sets": 3, "reps": "30 сек"},
            {"name": "Прыжки в приседе", "muscles": "ноги, кардио", "sets": 3, "reps": "10-12"},
        ]
    },
    "gym": {
        "chest": [
            {"name": "Жим штанги лёжа", "muscles": "грудные, трицепс", "sets": 4, "reps": "8-12"},
            {"name": "Жим гантелей на наклонной скамье", "muscles": "верх груди", "sets": 3, "reps": "10-12"},
            {"name": "Разводка гантелей лёжа", "muscles": "грудные", "sets": 3, "reps": "12-15"},
            {"name": "Сведение рук в кроссовере", "muscles": "грудные", "sets": 3, "reps": "12-15"},
        ],
        "back": [
            {"name": "Тяга верхнего блока", "muscles": "широчайшие", "sets": 4, "reps": "10-12"},
            {"name": "Тяга штанги в наклоне", "muscles": "широчайшие, трапеции", "sets": 3, "reps": "8-10"},
            {"name": "Тяга гантели одной рукой", "muscles": "широчайшие", "sets": 3, "reps": "10-12"},
            {"name": "Гиперэкстензия", "muscles": "разгибатели спины", "sets": 3, "reps": "12-15"},
        ],
        "legs": [
            {"name": "Приседания со штангой", "muscles": "квадрицепс, ягодицы", "sets": 4, "reps": "8-12"},
            {"name": "Жим ногами", "muscles": "квадрицепс", "sets": 3, "reps": "10-12"},
            {"name": "Выпады с гантелями", "muscles": "квадрицепс, ягодицы", "sets": 3, "reps": "10 на ногу"},
            {"name": "Сгибание ног в тренажёре", "muscles": "бицепс бедра", "sets": 3, "reps": "12-15"},
            {"name": "Разгибание ног в тренажёре", "muscles": "квадрицепс", "sets": 3, "reps": "12-15"},
            {"name": "Подъёмы на носки стоя", "muscles": "икры", "sets": 4, "reps": "15-20"},
        ],
        "shoulders": [
            {"name": "Жим гантелей сидя", "muscles": "дельты", "sets": 4, "reps": "10-12"},
            {"name": "Подъёмы гантелей в стороны", "muscles": "средние дельты", "sets": 3, "reps": "12-15"},
            {"name": "Подъёмы гантелей перед собой", "muscles": "передние дельты", "sets": 3, "reps": "10-12"},
            {"name": "Разведение в наклоне", "muscles": "задние дельты", "sets": 3, "reps": "12-15"},
        ],
        "arms": [
            {"name": "Подъём штанги на бицепс", "muscles": "бицепс", "sets": 3, "reps": "10-12"},
            {"name": "Молотки с гантелями", "muscles": "бицепс, брахиалис", "sets": 3, "reps": "10-12"},
            {"name": "Французский жим лёжа", "muscles": "трицепс", "sets": 3, "reps": "10-12"},
            {"name": "Разгибание рук на блоке", "muscles": "трицепс", "sets": 3, "reps": "12-15"},
        ],
        "core": [
            {"name": "Скручивания на римском стуле", "muscles": "пресс", "sets": 3, "reps": "15-20"},
            {"name": "Подъём ног в висе", "muscles": "нижний пресс", "sets": 3, "reps": "10-15"},
            {"name": "Планка", "muscles": "кор", "sets": 3, "reps": "45-60 сек"},
            {"name": "Скручивания в кроссовере", "muscles": "пресс", "sets": 3, "reps": "12-15"},
        ]
    }
}

# Training splits based on experience and days per week
SPLITS = {
    "beginner": {
        3: ["full_body", "full_body", "full_body"],
        4: ["upper", "lower", "upper", "lower"]
    },
    "intermediate": {
        3: ["push", "pull", "legs"],
        4: ["upper", "lower", "push", "pull"]
    },
    "advanced": {
        3: ["push", "pull", "legs"],
        4: ["chest_triceps", "back_biceps", "shoulders", "legs"]
    }
}

# Muscle groups for each split type
SPLIT_MUSCLES = {
    "full_body": ["chest", "back", "legs", "shoulders", "core"],
    "upper": ["chest", "back", "shoulders", "arms"],
    "lower": ["legs", "core"],
    "push": ["chest", "shoulders", "arms"],  # triceps focus
    "pull": ["back", "arms"],  # biceps focus
    "legs": ["legs", "core"],
    "chest_triceps": ["chest", "arms"],
    "back_biceps": ["back", "arms"],
    "shoulders": ["shoulders", "arms", "core"]
}


def get_exercises_for_muscle(location: str, muscle: str, count: int = 2) -> List[Dict]:
    """Get random exercises for a muscle group"""
    exercises = EXERCISES.get(location, {}).get(muscle, [])
    if len(exercises) <= count:
        return exercises
    return random.sample(exercises, count)


def generate_workout_day(location: str, split_type: str, experience: str) -> Dict:
    """Generate a single workout day"""
    muscles = SPLIT_MUSCLES.get(split_type, ["full_body"])
    exercises = []
    
    # Determine exercises per muscle based on experience
    exercises_per_muscle = {"beginner": 1, "intermediate": 2, "advanced": 2}.get(experience, 2)
    
    for muscle in muscles:
        muscle_exercises = get_exercises_for_muscle(location, muscle, exercises_per_muscle)
        exercises.extend(muscle_exercises)
    
    # Add cardio for weight loss
    if split_type == "full_body" and location == "home":
        cardio = get_exercises_for_muscle(location, "cardio", 1)
        exercises.extend(cardio)
    
    return {
        "split": split_type,
        "exercises": exercises
    }


def generate_workout_plan(
    goal: str,
    experience: str = "beginner",
    location: str = "home",
    days_per_week: int = 3
) -> Dict:
    """
    Generate complete workout plan
    
    Args:
        goal: 'lose', 'maintain', or 'gain' 
        experience: 'beginner', 'intermediate', or 'advanced'
        location: 'home' or 'gym'
        days_per_week: 3 or 4
    
    Returns:
        Complete workout plan with days and exercises
    """
    # Get appropriate split
    days_per_week = min(max(days_per_week, 3), 4)
    splits = SPLITS.get(experience, SPLITS["beginner"]).get(days_per_week, ["full_body"] * 3)
    
    # Day names based on count
    day_names = {
        3: ["Понедельник", "Среда", "Пятница"],
        4: ["Понедельник", "Вторник", "Четверг", "Пятница"]
    }
    
    plan = {
        "goal": goal,
        "experience": experience,
        "location": location,
        "days_per_week": days_per_week,
        "days": []
    }
    
    for i, split_type in enumerate(splits):
        day = generate_workout_day(location, split_type, experience)
        day["name"] = day_names[days_per_week][i]
        plan["days"].append(day)
    
    return plan


def format_workout_plan(plan: Dict) -> str:
    """Format workout plan as readable message"""
    goal_names = {
        "lose": "Похудение",
        "maintain": "Поддержание формы",
        "gain": "Набор массы"
    }
    location_names = {
        "home": "Дома",
        "gym": "В зале"
    }
    experience_names = {
        "beginner": "Новичок",
        "intermediate": "Средний",
        "advanced": "Продвинутый"
    }
    
    text = f"""
🏋️ *ВАША ПРОГРАММА ТРЕНИРОВОК*

🎯 Цель: *{goal_names.get(plan['goal'], plan['goal'])}*
📍 Место: *{location_names.get(plan['location'], plan['location'])}*
💪 Уровень: *{experience_names.get(plan['experience'], plan['experience'])}*
📅 Тренировок в неделю: *{plan['days_per_week']}*

"""
    
    for day in plan["days"]:
        split_name = day["split"].replace("_", " ").title()
        text += f"\n📆 *{day['name']}* — {split_name}\n"
        text += "─" * 25 + "\n"
        
        for ex in day["exercises"]:
            text += f"▫️ *{ex['name']}*\n"
            text += f"   {ex['sets']} × {ex['reps']} | {ex['muscles']}\n"
    
    text += "\n💡 *Рекомендации:*\n"
    text += "• Отдых между подходами: 60-90 сек\n"
    text += "• Обязательно разминка 5-10 мин\n"
    text += "• Прогрессивно увеличивайте нагрузку\n"
    
    return text


def format_single_day(day: Dict, day_number: int = 1) -> str:
    """Format single workout day"""
    text = f"📆 *День {day_number}: {day['name']}*\n"
    text += f"🎯 Тип: {day['split'].replace('_', ' ').title()}\n\n"
    
    for i, ex in enumerate(day["exercises"], 1):
        text += f"*{i}. {ex['name']}*\n"
        text += f"   └ {ex['sets']} × {ex['reps']}\n"
        text += f"   └ Мышцы: {ex['muscles']}\n\n"
    
    return text

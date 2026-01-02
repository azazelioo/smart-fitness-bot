"""
FSM States для дневника питания
"""

from aiogram.fsm.state import State, StatesGroup


class FoodDiaryStates(StatesGroup):
    """Состояния для добавления еды"""
    waiting_food_name = State()
    waiting_calories = State()
    waiting_protein = State()
    waiting_meal_type = State()


class ProfileStates(StatesGroup):
    """Состояния для настройки профиля"""
    waiting_gender = State()
    waiting_age = State()
    waiting_weight = State()
    waiting_height = State()
    waiting_activity = State()
    waiting_goal = State()


class WorkoutLogStates(StatesGroup):
    """Состояния для записи тренировки"""
    waiting_workout_name = State()
    waiting_workout_type = State()
    waiting_duration = State()
    waiting_calories_burned = State()

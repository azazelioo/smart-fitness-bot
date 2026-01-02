"""
FSM States для калькулятора калорий
"""

from aiogram.fsm.state import State, StatesGroup


class CalorieCalculatorStates(StatesGroup):
    """Состояния для расчёта калорий"""
    waiting_gender = State()
    waiting_age = State()
    waiting_weight = State()
    waiting_height = State()
    waiting_activity = State()
    waiting_goal = State()

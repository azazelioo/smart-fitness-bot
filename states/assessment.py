"""
FSM States для оценки боли/травмы
"""

from aiogram.fsm.state import State, StatesGroup


class AssessmentStates(StatesGroup):
    """Состояния FSM для процесса оценки боли"""
    
    # Шаг 1: Выбор области боли
    waiting_pain_location = State()
    
    # Шаг 2: Тип боли
    waiting_pain_type = State()
    
    # Шаг 3: Длительность
    waiting_pain_duration = State()
    
    # Шаг 4: Интенсивность (1-10)
    waiting_pain_intensity = State()
    
    # Шаг 5: Контекст (свободный текст)
    waiting_pain_context = State()
    
    # Анализ и результат
    processing_analysis = State()
    
    # Отслеживание восстановления
    tracking_recovery = State()

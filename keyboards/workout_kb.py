"""
Клавиатуры для раздела тренировок
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data import EXERCISES, WORKOUT_PROGRAMS


def get_workout_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню тренировок"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🎯 Упражнения по группам мышц",
            callback_data="exercises_by_muscle"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📋 Готовые программы",
            callback_data="workout_programs"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⚡ Быстрая тренировка 15 мин",
            callback_data="quick_workout"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🏠 Главное меню",
            callback_data="main_menu"
        )
    )
    
    return builder.as_markup()


def get_muscle_groups_keyboard() -> InlineKeyboardMarkup:
    """Группы мышц"""
    builder = InlineKeyboardBuilder()
    
    for key, data in EXERCISES.items():
        builder.row(
            InlineKeyboardButton(
                text=data["name"],
                callback_data=f"muscle:{key}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="workout_menu"
        )
    )
    
    return builder.as_markup()


def get_programs_keyboard() -> InlineKeyboardMarkup:
    """Список программ"""
    builder = InlineKeyboardBuilder()
    
    for key, program in WORKOUT_PROGRAMS.items():
        builder.row(
            InlineKeyboardButton(
                text=program["name"],
                callback_data=f"program:{key}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="workout_menu"
        )
    )
    
    return builder.as_markup()


def get_program_detail_keyboard() -> InlineKeyboardMarkup:
    """После просмотра программы"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📋 Другие программы",
            callback_data="workout_programs"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Меню тренировок",
            callback_data="workout_menu"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🏠 Главное меню",
            callback_data="main_menu"
        )
    )
    
    return builder.as_markup()

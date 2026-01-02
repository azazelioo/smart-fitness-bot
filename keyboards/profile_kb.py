"""
Клавиатуры для профиля
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Меню профиля"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 Моя статистика", callback_data="my_stats")
    )
    builder.row(
        InlineKeyboardButton(text="🧮 Обновить данные", callback_data="calorie_calculator")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_stats_keyboard() -> InlineKeyboardMarkup:
    """Меню статистики"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📝 Дневник питания", callback_data="food_diary")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="my_profile"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")
    )
    
    return builder.as_markup()

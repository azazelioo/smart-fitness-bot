"""
Клавиатуры для дневника питания
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_diary_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню дневника"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Добавить еду", callback_data="add_food")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Записи за сегодня", callback_data="view_today_food")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Моя статистика", callback_data="my_stats")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_meal_type_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа приёма пищи"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🌅 Завтрак", callback_data="meal:breakfast"),
        InlineKeyboardButton(text="☀️ Обед", callback_data="meal:lunch")
    )
    builder.row(
        InlineKeyboardButton(text="🌙 Ужин", callback_data="meal:dinner"),
        InlineKeyboardButton(text="🍎 Перекус", callback_data="meal:snack")
    )
    
    return builder.as_markup()


def get_skip_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    """Кнопка пропуска"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="⏭ Пропустить", callback_data=callback_data)
    )
    
    return builder.as_markup()


def get_after_food_keyboard() -> InlineKeyboardMarkup:
    """После добавления еды"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Добавить ещё", callback_data="add_food")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Дневник", callback_data="food_diary"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")
    )
    
    return builder.as_markup()

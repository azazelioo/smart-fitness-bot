"""
Клавиатуры для раздела питания
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_nutrition_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню питания"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🧮 Калькулятор калорий",
            callback_data="calorie_calculator"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📚 Советы по питанию",
            callback_data="nutrition_tips"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🏠 Главное меню",
            callback_data="main_menu"
        )
    )
    
    return builder.as_markup()


def get_nutrition_goals_keyboard() -> InlineKeyboardMarkup:
    """Цели питания"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🥗 Похудение", callback_data="nutrition_goal:weight_loss")
    )
    builder.row(
        InlineKeyboardButton(text="💪 Набор массы", callback_data="nutrition_goal:muscle_gain")
    )
    builder.row(
        InlineKeyboardButton(text="⚡ Энергия", callback_data="nutrition_goal:energy")
    )
    builder.row(
        InlineKeyboardButton(text="🧘 Восстановление", callback_data="nutrition_goal:recovery")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="nutrition_menu")
    )
    
    return builder.as_markup()


def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Выбор пола"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👨 Мужской", callback_data="gender:male"),
        InlineKeyboardButton(text="👩 Женский", callback_data="gender:female")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="nutrition_menu")
    )
    
    return builder.as_markup()


def get_activity_keyboard() -> InlineKeyboardMarkup:
    """Выбор активности"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🪑 Сидячий (офис, мало движения)",
            callback_data="activity:sedentary"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🚶 Лёгкая (1-3 тренировки/нед)",
            callback_data="activity:light"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🏃 Умеренная (3-5 тренировок/нед)",
            callback_data="activity:moderate"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🏋️ Высокая (6-7 тренировок/нед)",
            callback_data="activity:active"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⚡ Очень высокая (2 раза/день)",
            callback_data="activity:very_active"
        )
    )
    
    return builder.as_markup()


def get_goal_keyboard() -> InlineKeyboardMarkup:
    """Выбор цели"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📉 Похудеть", callback_data="cal_goal:lose")
    )
    builder.row(
        InlineKeyboardButton(text="⚖️ Поддерживать вес", callback_data="cal_goal:maintain")
    )
    builder.row(
        InlineKeyboardButton(text="📈 Набрать массу", callback_data="cal_goal:gain")
    )
    
    return builder.as_markup()


def get_after_calculation_keyboard() -> InlineKeyboardMarkup:
    """После расчёта калорий"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔄 Пересчитать", callback_data="calorie_calculator")
    )
    builder.row(
        InlineKeyboardButton(text="📚 Советы по питанию", callback_data="nutrition_tips")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()

"""
Inline клавиатуры для SmartFit Coach Bot
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import PainLocations, PainTypes, PainDurations


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🩹 Оценить боль/травму",
            callback_data="start_assessment"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🏋️ Тренировки",
            callback_data="workout_menu"
        ),
        InlineKeyboardButton(
            text="🥗 Питание",
            callback_data="nutrition_menu"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📝 Дневник",
            callback_data="food_diary"
        ),
        InlineKeyboardButton(
            text="👤 Профиль",
            callback_data="my_profile"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="💡 Совет дня",
            callback_data="get_tip"
        ),
        InlineKeyboardButton(
            text="ℹ️ Справка",
            callback_data="help"
        )
    )
    
    return builder.as_markup()


def get_pain_location_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора области боли"""
    builder = InlineKeyboardBuilder()
    
    # Разбиваем на 2 колонки
    locations = list(PainLocations.LOCATIONS.items())
    
    for i in range(0, len(locations), 2):
        row = []
        for j in range(2):
            if i + j < len(locations):
                key, text = locations[i + j]
                row.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=f"location:{key}"
                    )
                )
        builder.row(*row)
    
    # Кнопка отмены
    builder.row(
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel"
        )
    )
    
    return builder.as_markup()


def get_pain_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа боли"""
    builder = InlineKeyboardBuilder()
    
    for key, text in PainTypes.TYPES.items():
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"pain_type:{key}"
            )
        )
    
    # Назад и отмена
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="back_to_location"
        ),
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel"
        )
    )
    
    return builder.as_markup()


def get_pain_duration_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора длительности боли"""
    builder = InlineKeyboardBuilder()
    
    for key, text in PainDurations.DURATIONS.items():
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"duration:{key}"
            )
        )
    
    # Назад и отмена
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="back_to_pain_type"
        ),
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel"
        )
    )
    
    return builder.as_markup()


def get_pain_intensity_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора интенсивности боли (1-10)"""
    builder = InlineKeyboardBuilder()
    
    # Строка 1-5
    row1 = []
    for i in range(1, 6):
        emoji = "🟢" if i <= 3 else "🟡"
        row1.append(
            InlineKeyboardButton(
                text=f"{emoji} {i}",
                callback_data=f"intensity:{i}"
            )
        )
    builder.row(*row1)
    
    # Строка 6-10
    row2 = []
    for i in range(6, 11):
        emoji = "🟠" if i <= 7 else "🔴"
        row2.append(
            InlineKeyboardButton(
                text=f"{emoji} {i}",
                callback_data=f"intensity:{i}"
            )
        )
    builder.row(*row2)
    
    # Назад и отмена
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="back_to_duration"
        ),
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel"
        )
    )
    
    return builder.as_markup()


def get_skip_context_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для пропуска контекста"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="⏭ Пропустить",
            callback_data="skip_context"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="back_to_intensity"
        ),
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel"
        )
    )
    
    return builder.as_markup()


def get_after_analysis_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после анализа"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🔄 Новая оценка",
            callback_data="start_assessment"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📝 Сохранить в дневник",
            callback_data="save_to_diary"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🏠 Главное меню",
            callback_data="main_menu"
        )
    )
    
    return builder.as_markup()

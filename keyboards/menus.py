"""
Keyboard menus for the bot
"""
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def get_main_menu() -> ReplyKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Мой профиль"), KeyboardButton(text="🏋️ Тренировки")],
            [KeyboardButton(text="🍽 Питание"), KeyboardButton(text="📈 Статистика")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Gender selection keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 Мужской", callback_data="gender:male"),
                InlineKeyboardButton(text="👩 Женский", callback_data="gender:female")
            ]
        ]
    )
    return keyboard


def get_activity_keyboard() -> InlineKeyboardMarkup:
    """Activity level selection keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🪑 Минимальная (сидячая работа)", callback_data="activity:minimal")],
            [InlineKeyboardButton(text="🚶 Низкая (1-3 тр./неделю)", callback_data="activity:low")],
            [InlineKeyboardButton(text="🏃 Средняя (3-5 тр./неделю)", callback_data="activity:medium")],
            [InlineKeyboardButton(text="💪 Высокая (6-7 тр./неделю)", callback_data="activity:high")],
            [InlineKeyboardButton(text="🔥 Очень высокая (2 раза/день)", callback_data="activity:extreme")]
        ]
    )
    return keyboard


def get_goal_keyboard() -> InlineKeyboardMarkup:
    """Goal selection keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📉 Похудение", callback_data="goal:lose")],
            [InlineKeyboardButton(text="⚖️ Поддержание веса", callback_data="goal:maintain")],
            [InlineKeyboardButton(text="📈 Набор массы", callback_data="goal:gain")]
        ]
    )
    return keyboard


def get_location_keyboard() -> InlineKeyboardMarkup:
    """Training location selection keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏠 Дома", callback_data="location:home"),
                InlineKeyboardButton(text="🏋️ В зале", callback_data="location:gym")
            ]
        ]
    )
    return keyboard


def get_experience_keyboard() -> InlineKeyboardMarkup:
    """Experience level selection keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌱 Новичок", callback_data="experience:beginner")],
            [InlineKeyboardButton(text="🌿 Средний уровень", callback_data="experience:intermediate")],
            [InlineKeyboardButton(text="🌳 Продвинутый", callback_data="experience:advanced")]
        ]
    )
    return keyboard


def get_training_menu() -> InlineKeyboardMarkup:
    """Training menu keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Мой план тренировок", callback_data="training:my_plan")],
            [InlineKeyboardButton(text="🔄 Создать новый план", callback_data="training:new_plan")],
            [InlineKeyboardButton(text="📅 Тренировка на сегодня", callback_data="training:today")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main")]
        ]
    )
    return keyboard


def get_nutrition_menu() -> InlineKeyboardMarkup:
    """Nutrition menu keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📸 Сканировать еду", callback_data="nutrition:scan")],
            [InlineKeyboardButton(text="📝 Добавить вручную", callback_data="nutrition:manual")],
            [InlineKeyboardButton(text="📊 Дневник за сегодня", callback_data="nutrition:today")],
            [InlineKeyboardButton(text="🎯 Мои нормы КБЖУ", callback_data="nutrition:targets")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main")]
        ]
    )
    return keyboard


def get_food_confirm_keyboard(food_class: str) -> InlineKeyboardMarkup:
    """Keyboard to confirm adding food to diary"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Добавить в дневник", callback_data=f"food:add:{food_class}"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="food:cancel")
            ]
        ]
    )
    return keyboard


def get_food_alternatives_keyboard(predictions: list) -> InlineKeyboardMarkup:
    """Keyboard with food alternatives"""
    buttons = []
    for i, pred in enumerate(predictions):
        name = pred.get("name_ru", pred["food_class"])
        buttons.append([
            InlineKeyboardButton(
                text=f"➕ {name}", 
                callback_data=f"food:add:{pred['food_class']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="food:cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_meal_type_keyboard(food_class: str) -> InlineKeyboardMarkup:
    """Meal type selection keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌅 Завтрак", callback_data=f"meal:breakfast:{food_class}"),
                InlineKeyboardButton(text="🌞 Обед", callback_data=f"meal:lunch:{food_class}")
            ],
            [
                InlineKeyboardButton(text="🌆 Ужин", callback_data=f"meal:dinner:{food_class}"),
                InlineKeyboardButton(text="🍿 Перекус", callback_data=f"meal:snack:{food_class}")
            ]
        ]
    )
    return keyboard


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Generic confirm/cancel keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="confirm:yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data="confirm:no")
            ]
        ]
    )
    return keyboard


def get_days_per_week_keyboard() -> InlineKeyboardMarkup:
    """Days per week selection"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="3️⃣ 3 дня", callback_data="days:3"),
                InlineKeyboardButton(text="4️⃣ 4 дня", callback_data="days:4")
            ]
        ]
    )
    return keyboard


def get_weight_selection_keyboard(food_data: dict) -> InlineKeyboardMarkup:
    """Клавиатура выбора веса порции"""
    # Стандартные варианты веса
    weight_options = [50, 100, 150, 200, 250, 300]
    
    # Оценочный вес порции от нейросети (если есть)
    estimated = food_data.get("portion_grams", 100)
    
    buttons = []
    row = []
    
    for i, weight in enumerate(weight_options):
        # Отмечаем рекомендованный вес
        if abs(weight - estimated) < 25:
            text = f"⭐ {weight}г"
        else:
            text = f"{weight}г"
        
        row.append(InlineKeyboardButton(text=text, callback_data=f"weight:{weight}"))
        
        # По 3 кнопки в ряд
        if len(row) == 3:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    # Добавляем кнопку для ввода своего веса
    buttons.append([
        InlineKeyboardButton(text="✏️ Ввести свой вес", callback_data="weight:custom")
    ])
    
    # Кнопка отмены
    buttons.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="food:cancel")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_custom_weight_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для ввода своего веса"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="food:cancel")]
        ]
    )
    return keyboard


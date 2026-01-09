"""
Обработчики для питания и анализа еды
Включает распознавание еды по фото с нейросетью и выбор веса порции
"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import sys
sys.path.insert(0, str(__file__).replace('\\', '/').rsplit('/bot/', 1)[0])

from database import async_session, crud
from modules.food_analyzer import FoodRecognizer, get_food_info
from bot.keyboards.menus import (
    get_main_menu,
    get_nutrition_menu,
    get_food_alternatives_keyboard,
    get_meal_type_keyboard,
    get_weight_selection_keyboard,
    get_custom_weight_keyboard
)

router = Router()


class NutritionStates(StatesGroup):
    """FSM состояния для отслеживания питания"""
    waiting_for_photo = State()
    waiting_for_manual_input = State()
    waiting_for_weight = State()
    waiting_for_custom_weight = State()
    waiting_for_portion = State()


@router.message(F.text == "🍽 Питание")
async def show_nutrition_menu(message: Message):
    """Показать меню питания"""
    await message.answer(
        "🍽 *Питание*\n\nВыберите действие:",
        parse_mode="Markdown",
        reply_markup=get_nutrition_menu()
    )


@router.callback_query(F.data == "nutrition:scan")
async def start_food_scan(callback: CallbackQuery, state: FSMContext):
    """Начать сканирование еды - отправить фото"""
    await callback.message.edit_text(
        "📸 *Сканирование еды*\n\n"
        "Отправьте фото блюда, и я распознаю его с помощью нейросети!\n\n"
        "💡 _Для лучшего результата:_\n"
        "• Фотографируйте сверху\n"
        "• Хорошее освещение\n"
        "• Еда должна быть в фокусе",
        parse_mode="Markdown"
    )
    await state.set_state(NutritionStates.waiting_for_photo)
    await callback.answer()


@router.message(NutritionStates.waiting_for_photo, F.photo)
async def process_food_photo(message: Message, state: FSMContext, bot: Bot):
    """Обработать фото еды через нейросеть"""
    # Отправляем сообщение о процессе
    status_msg = await message.answer(
        "🔄 *Анализирую изображение...*\n\n"
        "Подождите, нейросеть распознаёт блюдо...",
        parse_mode="Markdown"
    )
    
    try:
        # Получаем фото
        photo = message.photo[-1]  # Берем самое большое разрешение
        file = await bot.get_file(photo.file_id)
        file_data = await bot.download_file(file.file_path)
        image_bytes = file_data.read()
        
        # Распознаем через нейросеть
        success, food_data, msg = await recognize_food_image(image_bytes)
        
        if success and food_data:
            # Сохраняем данные о еде в state
            await state.update_data(
                recognized_food=food_data,
                selected_weight=food_data.get("portion_grams", 100)
            )
            
            # Формируем сообщение с информацией
            text = f"""✅ *Блюдо распознано!*

🍽 *{food_data['name']}*
{f"_{food_data.get('description', '')}_" if food_data.get('description') else ""}

📊 *Пищевая ценность на 100г:*
🔥 Калории: *{food_data['calories_per_100g']:.0f} ккал*
🥩 Белки: *{food_data['protein_per_100g']:.1f} г*
🧈 Жиры: *{food_data['fat_per_100g']:.1f} г*
🍚 Углеводы: *{food_data['carbs_per_100g']:.1f} г*

🎯 Уверенность: *{food_data['confidence']:.0%}*

⚖️ *Выберите вес порции:*"""
            
            await status_msg.edit_text(
                text,
                parse_mode="Markdown",
                reply_markup=get_weight_selection_keyboard(food_data)
            )
            await state.set_state(NutritionStates.waiting_for_weight)
        else:
            # Ошибка распознавания
            await status_msg.edit_text(
                f"{msg}\n\n"
                "Попробуйте:\n"
                "• Сделать фото с лучшим освещением\n"
                "• Приблизить камеру к еде\n"
                "• Или добавьте еду вручную",
                parse_mode="Markdown",
                reply_markup=get_nutrition_menu()
            )
            await state.clear()
            
    except Exception as e:
        await status_msg.edit_text(
            f"❌ Произошла ошибка при распознавании.\n\n"
            f"Попробуйте ещё раз или добавьте еду вручную.",
            parse_mode="Markdown",
            reply_markup=get_nutrition_menu()
        )
        await state.clear()


@router.message(F.photo)
async def handle_photo_outside_state(message: Message, state: FSMContext, bot: Bot):
    """Обработка фото вне состояния сканирования"""
    # Автоматически запускаем распознавание
    await state.set_state(NutritionStates.waiting_for_photo)
    await process_food_photo(message, state, bot)


@router.callback_query(F.data.startswith("weight:"))
async def select_weight(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора веса порции"""
    weight_str = callback.data.split(":")[1]
    
    if weight_str == "custom":
        # Запрашиваем ввод своего веса
        await callback.message.edit_text(
            "⚖️ *Введите вес порции в граммах:*\n\n"
            "_Например: 175_",
            parse_mode="Markdown"
        )
        await state.set_state(NutritionStates.waiting_for_custom_weight)
        await callback.answer()
        return
    
    try:
        weight = int(weight_str)
    except ValueError:
        await callback.answer("Некорректный вес", show_alert=True)
        return
    
    # Получаем сохраненные данные
    data = await state.get_data()
    food_data = data.get("recognized_food")
    
    if not food_data:
        await callback.answer("Данные о еде не найдены", show_alert=True)
        await state.clear()
        return
    
    # Рассчитываем калории для выбранного веса
    calculated = calculate_calories_for_weight(food_data, weight)
    
    # Сохраняем выбранный вес
    await state.update_data(selected_weight=weight, calculated_nutrition=calculated)
    
    # Показываем результат и предлагаем выбрать прием пищи
    text = f"""✅ *{food_data['name']}*

⚖️ *Порция: {weight}г*

📊 *Пищевая ценность:*
🔥 Калории: *{calculated['calories']} ккал*
🥩 Белки: *{calculated['protein']:.1f} г*
🧈 Жиры: *{calculated['fat']:.1f} г*
🍚 Углеводы: *{calculated['carbs']:.1f} г*

🍽 *Выберите приём пищи:*"""
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_meal_type_keyboard_with_weight(food_data['name'], weight, calculated)
    )
    await callback.answer()


@router.message(NutritionStates.waiting_for_custom_weight)
async def process_custom_weight(message: Message, state: FSMContext):
    """Обработка ввода своего веса"""
    try:
        weight = float(message.text.strip().replace(",", "."))
        if weight <= 0 or weight > 5000:
            raise ValueError("Вес вне допустимого диапазона")
    except ValueError:
        await message.answer(
            "❌ Введите корректный вес в граммах (от 1 до 5000).\n\n"
            "_Например: 175_",
            parse_mode="Markdown"
        )
        return
    
    weight = round(weight)
    
    # Получаем сохраненные данные
    data = await state.get_data()
    food_data = data.get("recognized_food")
    
    if not food_data:
        await message.answer(
            "❌ Данные о еде не найдены. Отправьте новое фото.",
            reply_markup=get_nutrition_menu()
        )
        await state.clear()
        return
    
    # Рассчитываем калории
    calculated = calculate_calories_for_weight(food_data, weight)
    
    # Сохраняем
    await state.update_data(selected_weight=weight, calculated_nutrition=calculated)
    
    # Показываем результат
    text = f"""✅ *{food_data['name']}*

⚖️ *Порция: {weight}г*

📊 *Пищевая ценность:*
🔥 Калории: *{calculated['calories']} ккал*
🥩 Белки: *{calculated['protein']:.1f} г*
🧈 Жиры: *{calculated['fat']:.1f} г*
🍚 Углеводы: *{calculated['carbs']:.1f} г*

🍽 *Выберите приём пищи:*"""
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=get_meal_type_keyboard_with_weight(food_data['name'], weight, calculated)
    )


def get_meal_type_keyboard_with_weight(food_name: str, weight: int, nutrition: dict):
    """Клавиатура выбора приема пищи с сохранением данных"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    import json
    
    # Кодируем данные для callback
    # Ограничение callback_data - 64 байта, поэтому минимизируем
    calories = nutrition['calories']
    protein = nutrition['protein']
    fat = nutrition['fat']
    carbs = nutrition['carbs']
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌅 Завтрак", 
                    callback_data=f"savefood:breakfast:{weight}:{calories}"
                ),
                InlineKeyboardButton(
                    text="🌞 Обед", 
                    callback_data=f"savefood:lunch:{weight}:{calories}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌆 Ужин", 
                    callback_data=f"savefood:dinner:{weight}:{calories}"
                ),
                InlineKeyboardButton(
                    text="🍿 Перекус", 
                    callback_data=f"savefood:snack:{weight}:{calories}"
                )
            ],
            [
                InlineKeyboardButton(text="🔄 Изменить вес", callback_data="weight:change"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="food:cancel")
            ]
        ]
    )
    return keyboard


@router.callback_query(F.data == "weight:change")
async def change_weight(callback: CallbackQuery, state: FSMContext):
    """Изменить вес порции"""
    data = await state.get_data()
    food_data = data.get("recognized_food")
    
    if not food_data:
        await callback.answer("Данные не найдены", show_alert=True)
        return
    
    text = f"""🍽 *{food_data['name']}*

📊 *Пищевая ценность на 100г:*
🔥 Калории: *{food_data['calories_per_100g']:.0f} ккал*

⚖️ *Выберите вес порции:*"""
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_weight_selection_keyboard(food_data)
    )
    await state.set_state(NutritionStates.waiting_for_weight)
    await callback.answer()


@router.callback_query(F.data.startswith("savefood:"))
async def save_recognized_food(callback: CallbackQuery, state: FSMContext):
    """Сохранить распознанную еду в дневник"""
    parts = callback.data.split(":")
    meal_type = parts[1]
    weight = int(parts[2])
    calories = int(parts[3])
    
    # Получаем полные данные из state
    data = await state.get_data()
    food_data = data.get("recognized_food")
    calculated = data.get("calculated_nutrition")
    
    if not food_data or not calculated:
        await callback.answer("Данные не найдены", show_alert=True)
        await state.clear()
        return
    
    # Сохраняем в базу данных
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
        
        if user:
            await crud.create_food_log(
                session,
                user_id=user.id,
                food_name=food_data['name'],
                calories=calculated['calories'],
                protein=calculated['protein'],
                fat=calculated['fat'],
                carbs=calculated['carbs'],
                portion_grams=weight,
                meal_type=meal_type
            )
    
    meal_names = {
        "breakfast": "🌅 Завтрак",
        "lunch": "🌞 Обед",
        "dinner": "🌆 Ужин",
        "snack": "🍿 Перекус"
    }
    
    await callback.message.edit_text(
        f"✅ *{food_data['name']}* добавлено в дневник!\n\n"
        f"Приём пищи: {meal_names.get(meal_type, meal_type)}\n"
        f"⚖️ Порция: {weight}г\n"
        f"🔥 {calculated['calories']} ккал\n\n"
        f"Проверьте статистику в разделе «📈 Статистика»",
        parse_mode="Markdown"
    )
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    
    await state.clear()
    await callback.answer("Добавлено! ✅")


@router.callback_query(F.data.startswith("food:add:"))
async def add_food_to_diary(callback: CallbackQuery, state: FSMContext):
    """Добавить еду в дневник - сначала выбор веса"""
    food_class = callback.data.split(":")[2]
    
    food_info = get_food_info(food_class)
    if food_info:
        name = food_info.get("name_ru", food_class)
        calories = food_info.get("calories", 0)
        protein = food_info.get("protein", 0)
        fat = food_info.get("fat", 0)
        carbs = food_info.get("carbs", 0)
        
        # Сохраняем данные о еде для пересчёта
        food_data = {
            "name": name,
            "food_class": food_class,
            "calories_per_100g": calories,
            "protein_per_100g": protein,
            "fat_per_100g": fat,
            "carbs_per_100g": carbs,
            "portion_grams": food_info.get("portion", 100)
        }
        await state.update_data(
            recognized_food=food_data,
            selected_weight=100
        )
        
        text = f"""🍽 *{name}*

📊 *Пищевая ценность на 100г:*
🔥 Калории: *{calories} ккал*
🥩 Белки: *{protein} г*
🧈 Жиры: *{fat} г*
🍚 Углеводы: *{carbs} г*

⚖️ *Выберите вес порции:*"""
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_weight_selection_keyboard(food_data)
        )
        await state.set_state(NutritionStates.waiting_for_weight)
    else:
        await callback.answer("Блюдо не найдено", show_alert=True)
    
    await callback.answer()







@router.callback_query(F.data == "food:cancel")
async def cancel_food_add(callback: CallbackQuery, state: FSMContext):
    """Отменить добавление еды"""
    await state.clear()
    await callback.message.edit_text("❌ Отменено")
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    await callback.answer()


@router.callback_query(F.data == "nutrition:today")
async def show_today_nutrition(callback: CallbackQuery):
    """Показать статистику питания за сегодня"""
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
        
        if user is None:
            await callback.answer("Сначала заполните профиль", show_alert=True)
            return
        
        totals = await crud.get_daily_totals(session, user.id)
        logs = await crud.get_today_food_logs(session, user.id)
    
    target = user.target_calories or 2000
    eaten = totals["calories"]
    remaining = max(0, target - eaten)
    progress = min(100, int((eaten / target) * 100)) if target > 0 else 0
    
    # Прогресс бар
    filled = progress // 10
    bar = "█" * filled + "░" * (10 - filled)
    
    text = f"""
📊 *Дневник питания за сегодня*

🎯 Цель: {int(target)} ккал
🍽 Съедено: {int(eaten)} ккал
📉 Осталось: {int(remaining)} ккал

[{bar}] {progress}%

📋 *БЖУ:*
🥩 Белки: {totals['protein']:.1f} г
🧈 Жиры: {totals['fat']:.1f} г
🍚 Углеводы: {totals['carbs']:.1f} г

📝 *Приёмы пищи ({totals['meals_count']}):*
"""
    
    meal_icons = {
        "breakfast": "🌅",
        "lunch": "🌞",
        "dinner": "🌆",
        "snack": "🍿"
    }
    
    for log in logs[-5:]:  # Последние 5 записей
        icon = meal_icons.get(log.meal_type, "🍽")
        text += f"\n{icon} {log.food_name} — {int(log.calories)} ккал"
    
    if not logs:
        text += "\n_Пока пусто. Отправьте фото еды!_"
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_nutrition_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "nutrition:targets")
async def show_nutrition_targets(callback: CallbackQuery):
    """Показать целевые показатели питания"""
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
        
        if user is None or not user.is_registered:
            await callback.answer("Сначала заполните профиль", show_alert=True)
            return
        
        from modules.anthropometry import calculate_macros
        macros = calculate_macros(user.target_calories, user.goal)
    
    text = f"""
🎯 *Ваши целевые показатели*

🔥 Калории: *{int(user.target_calories)} ккал/день*

📋 *Распределение БЖУ:*
🥩 Белки: *{macros['protein']} г* (~{int(macros['protein']*4)} ккал)
🧈 Жиры: *{macros['fat']} г* (~{int(macros['fat']*9)} ккал)
🍚 Углеводы: *{macros['carbs']} г* (~{int(macros['carbs']*4)} ккал)

💡 _Эти значения рассчитаны на основе вашего профиля и цели_
"""
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_nutrition_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "nutrition:manual")
async def start_manual_input(callback: CallbackQuery, state: FSMContext):
    """Начать ручной ввод еды"""
    await callback.message.edit_text(
        "📝 *Ручной ввод*\n\nВведите название блюда для поиска:",
        parse_mode="Markdown"
    )
    await state.set_state(NutritionStates.waiting_for_manual_input)
    await callback.answer()


@router.message(NutritionStates.waiting_for_manual_input)
async def process_manual_search(message: Message, state: FSMContext):
    """Обработать поиск еды вручную"""
    query = message.text.strip()
    results = search_food_by_name(query)
    
    if results:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        buttons = []
        for r in results:
            name = r.get("name_ru", r["key"])
            calories = r.get("calories", 0)
            buttons.append([
                InlineKeyboardButton(
                    text=f"{name} ({calories} ккал/100г)",
                    callback_data=f"food:add:{r['key']}"
                )
            ])
        buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="food:cancel")])
        
        await message.answer(
            f"🔍 Найдено по запросу «{query}»:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
    else:
        await message.answer(
            f"❌ По запросу «{query}» ничего не найдено.\n\nПопробуйте другой запрос или отправьте фото.",
            reply_markup=get_nutrition_menu()
        )
        await state.clear()

"""
User registration and profile handlers
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import sys
sys.path.insert(0, str(__file__).replace('\\', '/').rsplit('/bot/', 1)[0])

from database import async_session, crud
from modules.anthropometry import calculate_all, format_nutrition_summary
from bot.keyboards.menus import (
    get_main_menu,
    get_gender_keyboard,
    get_activity_keyboard,
    get_goal_keyboard
)

router = Router()


class RegistrationStates(StatesGroup):
    """FSM states for registration"""
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_activity = State()
    waiting_for_goal = State()


@router.message(F.text == "📊 Мой профиль")
async def show_profile(message: Message, state: FSMContext):
    """Show profile or start registration"""
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        
        if user is None:
            user = await crud.create_user(
                session,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
        
        if user.is_registered and user.target_calories:
            # Show existing profile
            data = {
                "bmr": int(user.bmr or 0),
                "tdee": int(user.tdee or 0),
                "target_calories": int(user.target_calories or 0),
                "protein": 0,
                "fat": 0,
                "carbs": 0
            }
            
            # Recalculate macros
            if user.goal and user.target_calories:
                from modules.anthropometry import calculate_macros
                macros = calculate_macros(user.target_calories, user.goal)
                data.update(macros)
            
            profile_text = f"""
👤 *Ваш профиль*

📋 *Данные:*
• Пол: {'Мужской' if user.gender == 'male' else 'Женский'}
• Возраст: {user.age} лет
• Рост: {user.height} см
• Вес: {user.weight} кг

{format_nutrition_summary(data)}

🎯 Цель: {_get_goal_name(user.goal)}

_Для обновления данных нажмите кнопку ниже_
"""
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Обновить профиль", callback_data="profile:update")]
            ])
            
            await message.answer(profile_text, parse_mode="Markdown", reply_markup=keyboard)
        else:
            # Start registration
            await message.answer(
                "📝 *Давайте заполним ваш профиль!*\n\nВыберите ваш пол:",
                parse_mode="Markdown",
                reply_markup=get_gender_keyboard()
            )
            await state.set_state(RegistrationStates.waiting_for_gender)


@router.callback_query(F.data == "profile:update")
async def start_update_profile(callback: CallbackQuery, state: FSMContext):
    """Start profile update"""
    await callback.message.edit_text(
        "📝 *Обновление профиля*\n\nВыберите ваш пол:",
        parse_mode="Markdown",
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_gender)
    await callback.answer()


@router.callback_query(RegistrationStates.waiting_for_gender, F.data.startswith("gender:"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Process gender selection"""
    gender = callback.data.split(":")[1]
    await state.update_data(gender=gender)
    
    await callback.message.edit_text(
        f"✅ Пол: {'Мужской' if gender == 'male' else 'Женский'}\n\n📅 Введите ваш возраст (полных лет):",
        parse_mode="Markdown"
    )
    await state.set_state(RegistrationStates.waiting_for_age)
    await callback.answer()


@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    """Process age input"""
    try:
        age = int(message.text.strip())
        if age < 10 or age > 120:
            await message.answer("⚠️ Пожалуйста, введите корректный возраст (10-120 лет)")
            return
        
        await state.update_data(age=age)
        await message.answer(
            f"✅ Возраст: {age} лет\n\n📏 Введите ваш рост в сантиметрах:",
            parse_mode="Markdown"
        )
        await state.set_state(RegistrationStates.waiting_for_height)
    except ValueError:
        await message.answer("⚠️ Пожалуйста, введите число")


@router.message(RegistrationStates.waiting_for_height)
async def process_height(message: Message, state: FSMContext):
    """Process height input"""
    try:
        height = float(message.text.strip().replace(',', '.'))
        if height < 100 or height > 250:
            await message.answer("⚠️ Пожалуйста, введите корректный рост (100-250 см)")
            return
        
        await state.update_data(height=height)
        await message.answer(
            f"✅ Рост: {height} см\n\n⚖️ Введите ваш вес в килограммах:",
            parse_mode="Markdown"
        )
        await state.set_state(RegistrationStates.waiting_for_weight)
    except ValueError:
        await message.answer("⚠️ Пожалуйста, введите число")


@router.message(RegistrationStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    """Process weight input"""
    try:
        weight = float(message.text.strip().replace(',', '.'))
        if weight < 30 or weight > 300:
            await message.answer("⚠️ Пожалуйста, введите корректный вес (30-300 кг)")
            return
        
        await state.update_data(weight=weight)
        await message.answer(
            f"✅ Вес: {weight} кг\n\n🏃 Выберите ваш уровень физической активности:",
            parse_mode="Markdown",
            reply_markup=get_activity_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_activity)
    except ValueError:
        await message.answer("⚠️ Пожалуйста, введите число")


@router.callback_query(RegistrationStates.waiting_for_activity, F.data.startswith("activity:"))
async def process_activity(callback: CallbackQuery, state: FSMContext):
    """Process activity level selection"""
    activity = callback.data.split(":")[1]
    await state.update_data(activity_level=activity)
    
    await callback.message.edit_text(
        "✅ Уровень активности сохранён\n\n🎯 Выберите вашу цель:",
        parse_mode="Markdown",
        reply_markup=get_goal_keyboard()
    )
    await state.set_state(RegistrationStates.waiting_for_goal)
    await callback.answer()


@router.callback_query(RegistrationStates.waiting_for_goal, F.data.startswith("goal:"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    """Process goal selection and complete registration"""
    goal = callback.data.split(":")[1]
    data = await state.get_data()
    data["goal"] = goal
    
    # Calculate metabolism
    results = calculate_all(
        gender=data["gender"],
        weight=data["weight"],
        height=data["height"],
        age=data["age"],
        activity_level=data["activity_level"],
        goal=data["goal"]
    )
    
    # Save to database
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
        if user:
            await crud.update_user(
                session, user,
                gender=data["gender"],
                age=data["age"],
                height=data["height"],
                weight=data["weight"],
                activity_level=data["activity_level"],
                goal=data["goal"],
                bmr=results["bmr"],
                tdee=results["tdee"],
                target_calories=results["target_calories"],
                is_registered=True
            )
    
    await state.clear()
    
    success_message = f"""
✅ *Профиль успешно сохранён!*

{format_nutrition_summary(results)}

Теперь вы можете:
• 🏋️ Получить план тренировок
• 🍽 Анализировать питание по фото
• 📈 Отслеживать прогресс
"""
    
    await callback.message.edit_text(success_message, parse_mode="Markdown")
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu()
    )
    await callback.answer("Профиль сохранён! 🎉")


def _get_goal_name(goal: str) -> str:
    """Get human-readable goal name"""
    goals = {
        "lose": "📉 Похудение",
        "maintain": "⚖️ Поддержание веса",
        "gain": "📈 Набор массы"
    }
    return goals.get(goal, goal)

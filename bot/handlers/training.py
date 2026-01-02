"""
Training plan handlers
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import sys
sys.path.insert(0, str(__file__).replace('\\', '/').rsplit('/bot/', 1)[0])

from database import async_session, crud
from modules.training_generator import generate_workout_plan, format_workout_plan, format_single_day
from bot.keyboards.menus import (
    get_main_menu,
    get_training_menu,
    get_location_keyboard,
    get_experience_keyboard,
    get_days_per_week_keyboard
)

router = Router()


class TrainingStates(StatesGroup):
    """FSM states for training plan creation"""
    waiting_for_location = State()
    waiting_for_experience = State()
    waiting_for_days = State()


@router.message(F.text == "🏋️ Тренировки")
async def show_training_menu(message: Message):
    """Show training menu"""
    await message.answer(
        "🏋️ *Тренировки*\n\nВыберите действие:",
        parse_mode="Markdown",
        reply_markup=get_training_menu()
    )


@router.callback_query(F.data == "training:my_plan")
async def show_my_plan(callback: CallbackQuery):
    """Show current training plan"""
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
        
        if user is None:
            await callback.answer("Сначала заполните профиль", show_alert=True)
            return
        
        plan = await crud.get_active_workout_plan(session, user.id)
        
        if plan:
            plan_text = format_workout_plan(plan.plan_data)
            await callback.message.edit_text(
                plan_text,
                parse_mode="Markdown",
                reply_markup=get_training_menu()
            )
        else:
            await callback.message.edit_text(
                "📋 У вас пока нет плана тренировок.\n\nНажмите «Создать новый план» чтобы получить персональную программу!",
                reply_markup=get_training_menu()
            )
    
    await callback.answer()


@router.callback_query(F.data == "training:new_plan")
async def start_new_plan(callback: CallbackQuery, state: FSMContext):
    """Start creating new training plan"""
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
        
        if user is None or not user.is_registered:
            await callback.answer("Сначала заполните профиль", show_alert=True)
            return
        
        await state.update_data(goal=user.goal)
    
    await callback.message.edit_text(
        "🏋️ *Создание плана тренировок*\n\n📍 Где вы планируете тренироваться?",
        parse_mode="Markdown",
        reply_markup=get_location_keyboard()
    )
    await state.set_state(TrainingStates.waiting_for_location)
    await callback.answer()


@router.callback_query(TrainingStates.waiting_for_location, F.data.startswith("location:"))
async def process_location(callback: CallbackQuery, state: FSMContext):
    """Process location selection"""
    location = callback.data.split(":")[1]
    await state.update_data(location=location)
    
    await callback.message.edit_text(
        "✅ Место выбрано\n\n💪 Какой у вас уровень подготовки?",
        parse_mode="Markdown",
        reply_markup=get_experience_keyboard()
    )
    await state.set_state(TrainingStates.waiting_for_experience)
    await callback.answer()


@router.callback_query(TrainingStates.waiting_for_experience, F.data.startswith("experience:"))
async def process_experience(callback: CallbackQuery, state: FSMContext):
    """Process experience level selection"""
    experience = callback.data.split(":")[1]
    await state.update_data(experience=experience)
    
    await callback.message.edit_text(
        "✅ Уровень выбран\n\n📅 Сколько дней в неделю вы готовы тренироваться?",
        parse_mode="Markdown",
        reply_markup=get_days_per_week_keyboard()
    )
    await state.set_state(TrainingStates.waiting_for_days)
    await callback.answer()


@router.callback_query(TrainingStates.waiting_for_days, F.data.startswith("days:"))
async def process_days_and_create_plan(callback: CallbackQuery, state: FSMContext):
    """Process days selection and create training plan"""
    days = int(callback.data.split(":")[1])
    data = await state.get_data()
    
    # Generate plan
    plan = generate_workout_plan(
        goal=data.get("goal", "maintain"),
        experience=data["experience"],
        location=data["location"],
        days_per_week=days
    )
    
    # Save to database
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
        if user:
            await crud.update_user(
                session, user,
                training_location=data["location"],
                experience_level=data["experience"]
            )
            await crud.create_workout_plan(
                session,
                user_id=user.id,
                name=f"План на {days} дня",
                plan_data=plan
            )
    
    await state.clear()
    
    # Format and send plan
    plan_text = format_workout_plan(plan)
    
    await callback.message.edit_text(
        "✅ *План тренировок создан!*\n" + plan_text,
        parse_mode="Markdown"
    )
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu()
    )
    await callback.answer("План создан! 🎉")


@router.callback_query(F.data == "training:today")
async def show_today_workout(callback: CallbackQuery):
    """Show today's workout"""
    import datetime
    weekday = datetime.datetime.now().weekday()
    
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
        
        if user is None:
            await callback.answer("Сначала заполните профиль", show_alert=True)
            return
        
        plan = await crud.get_active_workout_plan(session, user.id)
        
        if plan and plan.plan_data:
            days = plan.plan_data.get("days", [])
            
            # Find workout for today based on weekday mapping
            day_mapping = {
                0: 0,  # Monday
                2: 1,  # Wednesday (if 3-day split)
                4: 2,  # Friday
                1: 0,  # Tuesday
                3: 1,  # Thursday
            }
            
            day_index = day_mapping.get(weekday, 0) % len(days) if days else 0
            
            if days and day_index < len(days):
                today = days[day_index]
                text = format_single_day(today, day_index + 1)
                await callback.message.edit_text(
                    f"📅 *Тренировка на сегодня*\n\n{text}",
                    parse_mode="Markdown",
                    reply_markup=get_training_menu()
                )
            else:
                await callback.message.edit_text(
                    "🌴 Сегодня день отдыха!\n\nВосстановление так же важно, как и тренировки.",
                    reply_markup=get_training_menu()
                )
        else:
            await callback.message.edit_text(
                "📋 Сначала создайте план тренировок",
                reply_markup=get_training_menu()
            )
    
    await callback.answer()


@router.callback_query(F.data == "menu:main")
async def back_to_main(callback: CallbackQuery):
    """Return to main menu"""
    await callback.message.delete()
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

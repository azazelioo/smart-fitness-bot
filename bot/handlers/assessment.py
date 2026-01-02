"""
Обработчики FSM для оценки боли/травмы
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import Messages, PainLocations
from states import AssessmentStates
from keyboards import (
    get_pain_location_keyboard,
    get_pain_type_keyboard,
    get_pain_duration_keyboard,
    get_pain_intensity_keyboard,
    get_after_analysis_keyboard,
    get_main_menu_keyboard,
)
from keyboards.inline import get_skip_context_keyboard
from services.openai_service import AssessmentData, get_injury_assessment

assessment_router = Router(name="assessment")


# ============ Начало оценки ============

@assessment_router.message(Command("assess"))
async def cmd_assess(message: Message, state: FSMContext):
    """Команда /assess - начать оценку"""
    await state.clear()
    await state.set_state(AssessmentStates.waiting_pain_location)
    
    await message.answer(
        Messages.START_ASSESSMENT,
        reply_markup=get_pain_location_keyboard(),
        parse_mode="Markdown"
    )


@assessment_router.callback_query(F.data == "start_assessment")
async def cb_start_assessment(callback: CallbackQuery, state: FSMContext):
    """Начало оценки через кнопку меню"""
    await state.clear()
    await state.set_state(AssessmentStates.waiting_pain_location)
    
    await callback.message.edit_text(
        Messages.START_ASSESSMENT,
        reply_markup=get_pain_location_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ============ Шаг 1: Выбор области боли ============

@assessment_router.callback_query(
    AssessmentStates.waiting_pain_location,
    F.data.startswith("location:")
)
async def cb_select_location(callback: CallbackQuery, state: FSMContext):
    """Выбор области боли"""
    location = callback.data.split(":")[1]
    
    await state.update_data(location=location)
    await state.set_state(AssessmentStates.waiting_pain_type)
    
    location_name = PainLocations.LOCATIONS.get(location, location)
    
    await callback.message.edit_text(
        Messages.PAIN_TYPE_QUESTION.format(location=location_name),
        reply_markup=get_pain_type_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ============ Шаг 2: Тип боли ============

@assessment_router.callback_query(F.data == "back_to_location")
async def cb_back_to_location(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору области"""
    await state.set_state(AssessmentStates.waiting_pain_location)
    
    await callback.message.edit_text(
        Messages.START_ASSESSMENT,
        reply_markup=get_pain_location_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@assessment_router.callback_query(
    AssessmentStates.waiting_pain_type,
    F.data.startswith("pain_type:")
)
async def cb_select_pain_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа боли"""
    pain_type = callback.data.split(":")[1]
    
    await state.update_data(pain_type=pain_type)
    await state.set_state(AssessmentStates.waiting_pain_duration)
    
    await callback.message.edit_text(
        Messages.PAIN_DURATION_QUESTION,
        reply_markup=get_pain_duration_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ============ Шаг 3: Длительность ============

@assessment_router.callback_query(F.data == "back_to_pain_type")
async def cb_back_to_pain_type(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору типа боли"""
    data = await state.get_data()
    location = data.get("location", "")
    location_name = PainLocations.LOCATIONS.get(location, location)
    
    await state.set_state(AssessmentStates.waiting_pain_type)
    
    await callback.message.edit_text(
        Messages.PAIN_TYPE_QUESTION.format(location=location_name),
        reply_markup=get_pain_type_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@assessment_router.callback_query(
    AssessmentStates.waiting_pain_duration,
    F.data.startswith("duration:")
)
async def cb_select_duration(callback: CallbackQuery, state: FSMContext):
    """Выбор длительности боли"""
    duration = callback.data.split(":")[1]
    
    await state.update_data(duration=duration)
    await state.set_state(AssessmentStates.waiting_pain_intensity)
    
    await callback.message.edit_text(
        Messages.PAIN_INTENSITY_QUESTION,
        reply_markup=get_pain_intensity_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ============ Шаг 4: Интенсивность ============

@assessment_router.callback_query(F.data == "back_to_duration")
async def cb_back_to_duration(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору длительности"""
    await state.set_state(AssessmentStates.waiting_pain_duration)
    
    await callback.message.edit_text(
        Messages.PAIN_DURATION_QUESTION,
        reply_markup=get_pain_duration_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@assessment_router.callback_query(
    AssessmentStates.waiting_pain_intensity,
    F.data.startswith("intensity:")
)
async def cb_select_intensity(callback: CallbackQuery, state: FSMContext):
    """Выбор интенсивности боли"""
    intensity = int(callback.data.split(":")[1])
    
    await state.update_data(intensity=intensity)
    await state.set_state(AssessmentStates.waiting_pain_context)
    
    await callback.message.edit_text(
        Messages.PAIN_CONTEXT_QUESTION,
        reply_markup=get_skip_context_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ============ Шаг 5: Контекст (опционально) ============

@assessment_router.callback_query(F.data == "back_to_intensity")
async def cb_back_to_intensity(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору интенсивности"""
    await state.set_state(AssessmentStates.waiting_pain_intensity)
    
    await callback.message.edit_text(
        Messages.PAIN_INTENSITY_QUESTION,
        reply_markup=get_pain_intensity_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@assessment_router.message(AssessmentStates.waiting_pain_context)
async def msg_context_input(message: Message, state: FSMContext):
    """Получение контекста (свободный текст)"""
    context = message.text.strip()[:500]  # Ограничиваем длину
    
    await state.update_data(context=context)
    await _perform_analysis(message, state)


@assessment_router.callback_query(
    AssessmentStates.waiting_pain_context,
    F.data == "skip_context"
)
async def cb_skip_context(callback: CallbackQuery, state: FSMContext):
    """Пропуск контекста"""
    await state.update_data(context=None)
    await callback.message.delete()
    await _perform_analysis(callback.message, state, from_callback=True)
    await callback.answer()


# ============ Анализ и результат ============

async def _perform_analysis(message: Message, state: FSMContext, from_callback: bool = False):
    """Выполнить анализ и показать результат"""
    await state.set_state(AssessmentStates.processing_analysis)
    
    # Показываем сообщение об анализе
    analyzing_msg = await message.answer(
        Messages.ANALYZING,
        parse_mode="Markdown"
    )
    
    # Получаем данные
    data = await state.get_data()
    
    assessment_data = AssessmentData(
        location=data.get("location", ""),
        pain_type=data.get("pain_type", ""),
        duration=data.get("duration", ""),
        intensity=data.get("intensity", 5),
        context=data.get("context")
    )
    
    # Получаем анализ от AI
    analysis = await get_injury_assessment(assessment_data)
    
    # Удаляем сообщение "Анализирую..."
    await analyzing_msg.delete()
    
    # Показываем результат
    result_text = Messages.ANALYSIS_COMPLETE.format(analysis=analysis)
    
    await message.answer(
        result_text,
        reply_markup=get_after_analysis_keyboard(),
        parse_mode="Markdown"
    )
    
    # Очищаем состояние
    await state.clear()


# ============ Действия после анализа ============

@assessment_router.callback_query(F.data == "save_to_diary")
async def cb_save_to_diary(callback: CallbackQuery):
    """Сохранить результат в дневник (заглушка)"""
    await callback.answer(
        "📝 Функция дневника будет доступна в следующей версии!",
        show_alert=True
    )


@assessment_router.callback_query(F.data == "my_progress")
async def cb_my_progress(callback: CallbackQuery):
    """Показать прогресс (заглушка)"""
    await callback.message.edit_text(
        "📊 **Ваш прогресс**\n\n"
        "_Вы еще не сохраняли оценки в дневник._\n\n"
        "Пройдите оценку боли и сохраните результат, чтобы отслеживать прогресс восстановления.",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

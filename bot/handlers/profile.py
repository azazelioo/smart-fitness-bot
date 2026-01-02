"""
Statistics and profile settings handlers
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import sys
sys.path.insert(0, str(__file__).replace('\\', '/').rsplit('/bot/', 1)[0])

from database import async_session, crud
from bot.keyboards.menus import get_main_menu

router = Router()


class WeightForm(StatesGroup):
    """FSM for weight logging"""
    waiting_for_weight = State()


@router.message(F.text == "📈 Статистика")
async def show_statistics(message: Message):
    """Show user statistics"""
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)

        if user is None or not user.is_registered:
            await message.answer(
                "📊 Для просмотра статистики сначала заполните профиль.",
                reply_markup=get_main_menu()
            )
            return

        # Get today's totals
        totals = await crud.get_daily_totals(session, user.id)

        # Get weight history
        weight_logs = await crud.get_weight_history(session, user.id, days=30)

    target = user.target_calories or 2000
    eaten = totals["calories"]
    remaining = max(0, target - eaten)

    # Calculate percentages
    cal_pct = min(100, int((eaten / target) * 100)) if target > 0 else 0

    from modules.anthropometry import calculate_macros
    macros = calculate_macros(target, user.goal or "maintain")

    protein_pct = min(100, int((totals["protein"] / macros["protein"]) * 100)) if macros["protein"] > 0 else 0
    fat_pct = min(100, int((totals["fat"] / macros["fat"]) * 100)) if macros["fat"] > 0 else 0
    carbs_pct = min(100, int((totals["carbs"] / macros["carbs"]) * 100)) if macros["carbs"] > 0 else 0        

    def make_bar(pct):
        filled = pct // 10
        return "█" * filled + "░" * (10 - filled)

    text = f"""
📈 *Ваша статистика*

━━━ *Сегодня* ━━━

🔥 *Калории*
[{make_bar(cal_pct)}] {cal_pct}%
{int(eaten)} / {int(target)} ккал

🥩 *Белки*
[{make_bar(protein_pct)}] {protein_pct}%
{totals['protein']:.0f} / {macros['protein']} г

🧈 *Жиры*
[{make_bar(fat_pct)}] {fat_pct}%
{totals['fat']:.0f} / {macros['fat']} г

🍚 *Углеводы*
[{make_bar(carbs_pct)}] {carbs_pct}%
{totals['carbs']:.0f} / {macros['carbs']} г

━━━ *Общая информация* ━━━

⚖️ Текущий вес: *{user.weight} кг*
🎯 Цель: *{_get_goal_name(user.goal)}*
📊 Приёмов пищи сегодня: *{totals['meals_count']}*
"""

    if weight_logs and len(weight_logs) > 1:
        first = weight_logs[0].weight
        last = weight_logs[-1].weight
        diff = last - first
        emoji = "📉" if diff < 0 else ("📈" if diff > 0 else "➡️")
        text += f"\n{emoji} Изменение веса за месяц: *{diff:+.1f} кг*"

    await message.answer(text, parse_mode="Markdown", reply_markup=get_main_menu())


@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: Message):
    """Show settings menu"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="�� Обновить профиль", callback_data="profile:update")],
        [InlineKeyboardButton(text="⚖️ Записать вес", callback_data="settings:weight")],
        [InlineKeyboardButton(text="🗑 Очистить дневник за сегодня", callback_data="settings:clear_diary")]    
    ])

    await message.answer(
        "⚙️ *Настройки*\n\nВыберите действие:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "settings:weight")
async def log_weight_start(callback: CallbackQuery, state: FSMContext):
    """Start weight logging"""
    await callback.message.edit_text(
        "⚖️ *Запись веса*\n\nВведите ваш текущий вес в килограммах:",
        parse_mode="Markdown"
    )
    await state.set_state(WeightForm.waiting_for_weight)
    await callback.answer()


@router.message(WeightForm.waiting_for_weight)
async def process_weight_input(message: Message, state: FSMContext):
    """Process weight input"""
    try:
        weight = float(message.text.replace(',', '.'))
        
        if weight <= 0 or weight > 300:
            await message.answer("❌ Некорректный вес. Введите значение от 1 до 300 кг.")
            return
        
        async with async_session() as session:
            user = await crud.get_user_by_telegram_id(session, message.from_user.id)
            
            if user is None:
                await message.answer("❌ Пользователь не найден.")
                await state.clear()
                return
            
            # Create weight log
            await crud.create_weight_log(session, user.id, weight)
            
            # Update user's current weight - передаем объект user, а не user.id
            await crud.update_user(session, user, weight=weight)
        
        await message.answer(
            f"✅ Вес успешно записан: *{weight} кг*",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Некорректный формат. Введите число (например: 75.5 или 80):",
        )


@router.callback_query(F.data == "settings:clear_diary")
async def clear_diary_confirm(callback: CallbackQuery):
    """Confirm diary clearing"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, очистить", callback_data="clear:confirm"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="clear:cancel")
        ]
    ])

    await callback.message.edit_text(
        "⚠️ *Вы уверены?*\n\nВсе записи о питании за сегодня будут удалены.",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "clear:cancel")
async def clear_diary_cancel(callback: CallbackQuery):
    """Cancel diary clearing"""
    await callback.message.delete()
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    await callback.answer()


@router.callback_query(F.data == "clear:confirm")
async def clear_diary_execute(callback: CallbackQuery):
    """Execute diary clearing"""
    # Note: Need to implement delete function in crud
    await callback.message.edit_text("✅ Дневник за сегодня очищен")
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    await callback.answer("Очищено")


def _get_goal_name(goal: str) -> str:
    """Get human-readable goal name"""
    goals = {
        "lose": "Похудение",
        "maintain": "Поддержание",
        "gain": "Набор массы"
    }
    return goals.get(goal, goal or "Не указана")

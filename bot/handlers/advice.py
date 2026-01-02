"""
Обработчики для советов и рекомендаций
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import Messages
from keyboards import get_main_menu_keyboard
from services.openai_service import get_recovery_tip

advice_router = Router(name="advice")


@advice_router.message(Command("tips"))
async def cmd_tips(message: Message):
    """Команда /tips - получить совет"""
    tip = await get_recovery_tip()
    
    await message.answer(
        Messages.RECOVERY_TIP.format(tip=tip),
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


@advice_router.callback_query(F.data == "get_tip")
async def cb_get_tip(callback: CallbackQuery):
    """Получить совет через кнопку"""
    tip = await get_recovery_tip()
    
    await callback.message.edit_text(
        Messages.RECOVERY_TIP.format(tip=tip),
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

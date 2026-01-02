"""
Start and help command handlers
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

import sys
sys.path.insert(0, str(__file__).replace('\\', '/').rsplit('/bot/', 1)[0])

from database import async_session, crud
from bot.keyboards.menus import get_main_menu

router = Router()


WELCOME_MESSAGE = """
🏋️ *Добро пожаловать в Smart Fitness Assistant!*

Я ваш персональный фитнес-помощник. Вот что я умею:

📊 *Профиль* — рассчитаю вашу норму калорий и БЖУ
🏋️ *Тренировки* — составлю индивидуальную программу
🍽 *Питание* — проанализирую еду по фото
📈 *Статистика* — отслеживание прогресса

Давайте начнём! 👇
"""

HELP_MESSAGE = """
❓ *Справка по Smart Fitness Assistant*

*Основные команды:*
/start — Начать работу с ботом
/help — Показать эту справку
/profile — Мой профиль и показатели
/plan — Мой тренировочный план
/stats — Статистика за сегодня

*Как пользоваться:*

1️⃣ *Профиль*
Заполните анкету (пол, возраст, рост, вес, цель)
Бот рассчитает вашу норму калорий

2️⃣ *Тренировки* 
Выберите место (дом/зал) и уровень
Получите персональный план на неделю

3️⃣ *Питание*
Отправьте фото блюда 📸
Бот определит что это и покажет КБЖУ
Добавьте в дневник одним нажатием

4️⃣ *Статистика*
Смотрите сколько калорий съели за день
Сравнивайте с целевыми показателями

💡 _Совет: используйте кнопки меню для быстрой навигации_
"""


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        
        if user is None:
            # Create new user
            user = await crud.create_user(
                session,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
            
            await message.answer(
                WELCOME_MESSAGE + "\n\n📝 *Для начала давайте заполним ваш профиль!*\n\nНажмите «📊 Мой профиль»",
                parse_mode="Markdown",
                reply_markup=get_main_menu()
            )
        else:
            name = user.first_name or user.username or "Друг"
            await message.answer(
                f"👋 С возвращением, *{name}*!\n\nВыберите действие:",
                parse_mode="Markdown",
                reply_markup=get_main_menu()
            )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    await message.answer(HELP_MESSAGE, parse_mode="Markdown")


@router.message(F.text == "❓ Помощь")
async def btn_help(message: Message):
    """Handle help button"""
    await message.answer(HELP_MESSAGE, parse_mode="Markdown")

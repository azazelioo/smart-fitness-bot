"""
SmartFit Coach Bot - Configuration
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./fitness_bot.db")
OPENAI_MODEL = "gpt-4o-mini"

@dataclass
class BotConfig:
    """Конфигурация бота"""
    bot_token: str = BOT_TOKEN
    BOT_TOKEN: str = BOT_TOKEN
    DATABASE_URL: str = DATABASE_URL
    openai_api_key: Optional[str] = OPENAI_API_KEY or GROQ_API_KEY
    gemini_api_key: Optional[str] = GEMINI_API_KEY
    openai_model: str = OPENAI_MODEL

    ACTIVITY_LEVELS = {
        "minimal": 1.2,
        "low": 1.375,
        "medium": 1.55,
        "high": 1.725,
        "extreme": 1.9
    }

    GOALS = {
        "lose": -500,
        "maintain": 0,
        "gain": 300
    }

    MACROS = {
        "lose": {"protein": 0.30, "fat": 0.25, "carbs": 0.45},
        "maintain": {"protein": 0.25, "fat": 0.30, "carbs": 0.45},
        "gain": {"protein": 0.25, "fat": 0.25, "carbs": 0.50}
    }

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key and len(self.gemini_api_key) > 5)

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key and len(self.openai_api_key) > 10)

config = BotConfig()

class Messages:
    WELCOME = """🏋️ **Добро пожаловать в SmartFit Coach!**

Я - ваш персональный AI-помощник по фитнесу:

🩹 **Оценка травм** - AI-анализ боли с рекомендациями
🏋️ **Тренировки** - упражнения и готовые программы
🥗 **Питание** - калькулятор калорий и советы
💡 **Советы** - ежедневные рекомендации по восстановлению"""

    START_ASSESSMENT = "📍 **Давайте оценим вашу проблему**\n\nГде вы чувствуете боль или дискомфорт?"
    PAIN_TYPE_QUESTION = "🔍 **Опишите характер боли в области: {location}**"
    PAIN_DURATION_QUESTION = "⏱ **Как долго беспокоит эта проблема?**"
    PAIN_INTENSITY_QUESTION = "📈 **Оцените интенсивность боли по шкале от 1 до 10:**"
    PAIN_CONTEXT_QUESTION = "🏃 **Что вызывает или усиливает боль?**"
    ANALYZING = "🔄 **Анализирую ваши симптомы...**"
    ANALYSIS_COMPLETE = "✅ **Анализ завершен!**\n\n{analysis}"

class PainLocations:
    LOCATIONS = {
        "knee": "🦵 Колено",
        "back": "�� Спина",
        "shoulder": "💪 Плечо",
        "ankle": "🦶 Голеностоп",
        "elbow": "💪 Локоть",
        "hip": "🦴 Бедро/Таз",
        "neck": "👤 Шея",
        "wrist": "✋ Запястье",
    }

class PainTypes:
    TYPES = {
        "sharp": "⚡ Острая/резкая",
        "dull": "😐 Тупая/ноющая",
        "burning": "🔥 Жгучая",
        "throbbing": "💓 Пульсирующая",
    }

class PainDurations:
    DURATIONS = {
        "today": "📅 Сегодня",
        "days": "📆 Несколько дней",
        "weeks": "🗓 Несколько недель",
        "months": "📊 Больше месяца",
    }

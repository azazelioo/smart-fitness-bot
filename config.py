"""
SmartFit Coach Bot - Configuration
Конфигурация бота для оценки спортивных травм и восстановления
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token (из переменной окружения для безопасности)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# OpenAI API Key (оставьте пустым для использования заглушки)
GROQ_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")

# Google Gemini API Key
GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")

# OpenAI Model
OPENAI_MODEL = "gpt-4o-mini"


@dataclass
class BotConfig:
    """Конфигурация бота"""
    bot_token: str = BOT_TOKEN
    openai_api_key: Optional[str] = GROQ_API_KEY
    gemini_api_key: Optional[str] = GEMINI_API_KEY
    openai_model: str = OPENAI_MODEL
    
    # Activity coefficients for TDEE calculation
    ACTIVITY_LEVELS = {
        "minimal": 1.2,
        "low": 1.375,
        "medium": 1.55,
        "high": 1.725,
        "extreme": 1.9
    }
    
    # Goals calorie adjustments
    GOALS = {
        "lose": -500,
        "maintain": 0,
        "gain": 300
    }
    
    # Macros distribution (percentage)
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
        """Проверяет наличие OpenAI API ключа"""
        return bool(self.openai_api_key and len(self.openai_api_key) > 10)


# Глобальный экземпляр конфигурации
config = BotConfig()


# Тексты бота
class Messages:
    """Сообщения бота на русском языке"""
    
    WELCOME = """
🏋️ **Добро пожаловать в SmartFit Coach!**

Я - ваш персональный AI-помощник по фитнесу:

🩹 **Оценка травм** - AI-анализ боли с рекомендациями
🏋️ **Тренировки** - упражнения и готовые программы
🥗 **Питание** - калькулятор калорий и советы
💡 **Советы** - ежедневные рекомендации по восстановлению

_Выберите действие из меню:_
"""

    START_ASSESSMENT = """
📍 **Давайте оценим вашу проблему**

Где вы чувствуете боль или дискомфорт?
Выберите область тела:
"""

    PAIN_TYPE_QUESTION = """
🔍 **Опишите характер боли в области: {location}**

Какой тип боли вы испытываете?
"""

    PAIN_DURATION_QUESTION = """
⏱ **Как долго беспокоит эта проблема?**

Выберите период:
"""

    PAIN_INTENSITY_QUESTION = """
📈 **Оцените интенсивность боли по шкале от 1 до 10:**

1-3: Легкая (терпимый дискомфорт)
4-6: Умеренная (заметно влияет на активность)
7-10: Сильная (значительно ограничивает движения)
"""

    PAIN_CONTEXT_QUESTION = """
🏃 **Что вызывает или усиливает боль?**

Опишите ситуацию:
- Когда появилась боль?
- При каких движениях усиливается?
- Была ли травма или удар?
"""

    ANALYZING = """
🔄 **Анализирую ваши симптомы...**

Пожалуйста, подождите несколько секунд.
"""

    ANALYSIS_COMPLETE = """
✅ **Анализ завершен!**

{analysis}

---
⚠️ _Это не замена консультации врача. При сильной боли или подозрении на серьезную травму обратитесь к специалисту!_

Что делаем дальше?
"""

    EMERGENCY_WARNING = """
🚨 **ВНИМАНИЕ! Рекомендуется обратиться к врачу!**

На основе ваших симптомов я рекомендую:
- Немедленно прекратить физическую активность
- Обратиться к травматологу или ортопеду
- Не пытаться самостоятельно лечить эту проблему

{reason}
"""
    
    RECOVERY_TIP = """
💡 **Совет дня по восстановлению:**

{tip}
"""
    
    HELP_TEXT = """
ℹ️ **Справка по SmartFit Coach**

**Доступные команды:**
/start - Главное меню
/assess - Оценить боль/травму
/workout - Тренировки и упражнения
/nutrition - Питание и калории
/tips - Совет по восстановлению
/help - Эта справка

**Основные функции:**
🩹 Оценка травм с AI-рекомендациями
🏋️ База упражнений по группам мышц
📋 Готовые программы тренировок
🧮 Калькулятор калорий и макросов
📚 Советы по питанию

**О боте:**
SmartFit Coach - AI-помощник для фитнеса. Бот не заменяет врача!
"""


# Данные для опросника
class PainLocations:
    """Местоположения боли"""
    
    LOCATIONS = {
        "knee": "🦵 Колено",
        "back": "🔙 Спина",
        "shoulder": "💪 Плечо",
        "ankle": "🦶 Голеностоп",
        "elbow": "💪 Локоть",
        "hip": "🦴 Бедро/Таз",
        "neck": "👤 Шея",
        "wrist": "✋ Запястье",
        "thigh": "🦵 Бедро",
        "calf": "🦵 Голень",
    }
    
    LOCATIONS_RU = {
        "knee": "колено",
        "back": "спина",
        "shoulder": "плечо",
        "ankle": "голеностоп",
        "elbow": "локоть",
        "hip": "бедро/таз",
        "neck": "шея",
        "wrist": "запястье",
        "thigh": "бедро",
        "calf": "голень",
    }


class PainTypes:
    """Типы боли"""
    
    TYPES = {
        "sharp": "⚡ Острая/резкая",
        "dull": "😐 Тупая/ноющая",
        "burning": "🔥 Жгучая",
        "throbbing": "💓 Пульсирующая",
        "stiff": "🧊 Скованность",
        "radiating": "↗️ Отдающая в другие области",
    }


class PainDurations:
    """Длительность боли"""
    
    DURATIONS = {
        "today": "📅 Сегодня (менее 24 часов)",
        "days": "📆 Несколько дней (2-7 дней)",
        "weeks": "🗓 Несколько недель",
        "months": "📊 Больше месяца",
        "chronic": "⏳ Хроническая (повторяется регулярно)",
    }

"""
OpenAI Service для анализа травм и рекомендаций
"""

import asyncio
from typing import Optional
from dataclasses import dataclass

from config import config, PainLocations, PainTypes, PainDurations


@dataclass
class AssessmentData:
    """Данные оценки боли"""
    location: str
    pain_type: str
    duration: str
    intensity: int
    context: Optional[str] = None
    
    def get_location_ru(self) -> str:
        """Получить локацию на русском"""
        return PainLocations.LOCATIONS_RU.get(self.location, self.location)
    
    def get_pain_type_ru(self) -> str:
        """Получить тип боли на русском"""
        return PainTypes.TYPES.get(self.pain_type, self.pain_type)
    
    def get_duration_ru(self) -> str:
        """Получить длительность на русском"""
        return PainDurations.DURATIONS.get(self.duration, self.duration)


class OpenAIService:
    """Сервис для работы с OpenAI API"""
    
    def __init__(self):
        self.api_key = config.openai_api_key
        self.model = config.openai_model
        self._client = None
    
    @property
    def is_available(self) -> bool:
        """Проверить доступность OpenAI"""
        return config.has_openai
    
    async def _get_client(self):
        """Получить OpenAI клиент (ленивая инициализация)"""
        if not self.is_available:
            return None
            
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                return None
        
        return self._client
    
    async def analyze_injury(self, data: AssessmentData) -> str:
        """Анализировать данные о травме и дать рекомендации"""
        
        client = await self._get_client()
        
        if client is None:
            # Используем заглушку если OpenAI недоступен
            return await self._mock_analysis(data)
        
        try:
            prompt = self._build_prompt(data)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Ты - опытный спортивный физиотерапевт и тренер по фитнесу. 
Твоя задача - проанализировать симптомы пользователя и дать рекомендации.

Ответ должен содержать:
1. **Возможная причина** - что это может быть (1-2 предложения)
2. **Рекомендации по первой помощи** - что делать прямо сейчас
3. **План восстановления** - конкретные действия на ближайшие дни
4. **Когда к врачу** - признаки, при которых нужно обратиться к специалисту

Отвечай на русском языке. Будь конкретен и практичен.
НЕ ставь диагнозы - только предположения и рекомендации.
Всегда рекомендуй обратиться к врачу при сильной боли."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return await self._mock_analysis(data)
    
    def _build_prompt(self, data: AssessmentData) -> str:
        """Построить промпт для OpenAI"""
        context_text = f"\nДополнительный контекст: {data.context}" if data.context else ""
        
        return f"""Проанализируй следующие симптомы:

**Область боли:** {data.get_location_ru()}
**Характер боли:** {data.get_pain_type_ru()}
**Длительность:** {data.get_duration_ru()}
**Интенсивность по шкале 1-10:** {data.intensity}{context_text}

Дай рекомендации по восстановлению и предупреди о рисках."""
    
    async def _mock_analysis(self, data: AssessmentData) -> str:
        """Заглушка для анализа без OpenAI"""
        
        # Имитация задержки "анализа"
        await asyncio.sleep(1)
        
        is_severe = data.intensity >= 7
        is_chronic = data.duration in ["months", "chronic"]
        is_acute = data.duration in ["today", "days"]
        
        # Базовые рекомендации по зонам
        location_advice = {
            "knee": {
                "cause": "боль в колене может быть связана с перенапряжением связок, воспалением сухожилий или начальной стадией артрита",
                "first_aid": "Приложите лёд на 15-20 минут, избегайте нагрузок на ногу",
                "recovery": "Выполняйте легкую растяжку квадрицепса, укрепляйте мышцы бедра изометрическими упражнениями",
                "exercises": "Подъёмы прямой ноги лёжа, полуприседания у стены"
            },
            "back": {
                "cause": "боль в спине часто вызвана мышечным спазмом, неправильной осанкой или перенапряжением при тренировках",
                "first_aid": "Лягте на спину с согнутыми коленями, приложите тепло к болезненной области",
                "recovery": "Делайте упражнения на растяжку и укрепление мышц кора, избегайте длительного сидения",
                "exercises": "Кошка-корова, планка на локтях (30 сек), мёртвый жук"
            },
            "shoulder": {
                "cause": "боль в плече может указывать на воспаление вращательной манжеты, импинджмент-синдром или мышечное напряжение",
                "first_aid": "Избегайте движений над головой, приложите лёд",
                "recovery": "Выполняйте упражнения с резинкой на внешнюю ротацию, растягивайте грудные мышцы",
                "exercises": "Маятниковые движения рукой, скольжение по стене, растяжка doorway"
            },
            "ankle": {
                "cause": "боль в голеностопе обычно связана с растяжением связок, тендинитом ахилла или перегрузкой при беге",
                "first_aid": "Протокол RICE: покой, лёд, компрессия, возвышенное положение",
                "recovery": "Укрепляйте мышцы голени, работайте над балансом",
                "exercises": "Подъёмы на носки, балансирование на одной ноге, алфавит стопой"
            }
        }
        
        # Получаем рекомендации для локации или общие
        default_advice = {
            "cause": "боль может быть связана с мышечным напряжением, воспалением или перегрузкой",
            "first_aid": "Обеспечьте покой, приложите лёд на 15-20 минут",
            "recovery": "Постепенно возвращайтесь к активности, выполняйте легкую растяжку",
            "exercises": "Начните с активной мобилизации и лёгкой растяжки"
        }
        
        advice = location_advice.get(data.location, default_advice)
        
        # Формируем ответ
        warning = ""
        if is_severe:
            warning = "\n\n⚠️ **ВНИМАНИЕ:** При интенсивности боли 7+ рекомендую обратиться к врачу для исключения серьёзной травмы!"
        
        chronic_note = ""
        if is_chronic:
            chronic_note = "\n\n📌 **Важно:** Хроническая боль требует комплексного подхода. Рекомендую консультацию физиотерапевта для составления индивидуальной программы."
        
        acute_note = ""
        if is_acute and data.pain_type == "sharp":
            acute_note = "\n\n🔴 **Острая боль:** При недавней острой травме первые 48-72 часа соблюдайте протокол RICE и избегайте нагрузок."
        
        return f"""**🔍 Возможная причина:**
{advice['cause'].capitalize()}.

**🩹 Первая помощь:**
{advice['first_aid']}

**📋 План восстановления (ближайшие 3-7 дней):**
- День 1-2: Покой и противовоспалительные меры
- День 3-5: {advice['recovery']}
- День 5-7: Постепенное возвращение к лёгкой активности

**💪 Рекомендуемые упражнения:**
{advice['exercises']}

**🏥 Когда обратиться к врачу:**
- Боль не уменьшается после 3-5 дней отдыха
- Появился отёк, покраснение или повышение температуры
- Ограничение подвижности сохраняется
- Боль возникла после травмы или удара{warning}{chronic_note}{acute_note}"""


async def get_injury_assessment(data: AssessmentData) -> str:
    """Получить оценку травмы (удобная функция)"""
    service = OpenAIService()
    return await service.analyze_injury(data)


async def get_recovery_tip() -> str:
    """Получить случайный совет по восстановлению"""
    import random
    
    tips = [
        "💧 **Гидратация:** Пейте 2-3 литра воды в день. Обезвоживание замедляет восстановление мышц.",
        "😴 **Сон:** 7-9 часов качественного сна - лучшее лекарство для восстановления. Именно во сне выделяется гормон роста.",
        "🧘 **Растяжка:** 10-15 минут растяжки после тренировки уменьшает мышечную боль на 30%.",
        "🥗 **Белок:** Потребляйте 1.6-2.2 г белка на кг веса в день для оптимального восстановления.",
        "❄️ **Контрастный душ:** Чередование холодной и горячей воды улучшает кровообращение и ускоряет восстановление.",
        "🎯 **Активное восстановление:** Лёгкая ходьба или плавание в дни отдыха лучше полного бездействия.",
        "🧠 **Стресс:** Хронический стресс повышает кортизол и замедляет восстановление. Практикуйте медитацию.",
        "⏰ **Отдых между тренировками:** Мышечной группе нужно 48-72 часа отдыха перед следующей нагрузкой.",
        "🍌 **Калий и магний:** Бананы, орехи и тёмный шоколад помогают предотвратить судороги.",
        "🔄 **Прогрессия:** Увеличивайте нагрузку не более чем на 10% в неделю для профилактики травм."
    ]
    
    return random.choice(tips)

"""
Модуль распознавания еды с использованием Groq API (Llama 4 Scout)
"""
import os
import logging
import base64
import aiohttp
import json
import re
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NutritionInfo:
    """Информация о пищевой ценности продукта"""
    name: str
    name_en: str
    calories_per_100g: float
    protein_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float
    portion_grams: float = 100.0
    confidence: float = 0.0
    description: str = ""

    def calculate_for_weight(self, weight_grams: float) -> Dict:
        """Рассчитать БЖУ для указанного веса"""
        multiplier = weight_grams / 100.0
        return {
            "name": self.name,
            "weight_grams": weight_grams,
            "calories": round(self.calories_per_100g * multiplier),
            "protein": round(self.protein_per_100g * multiplier, 1),
            "fat": round(self.fat_per_100g * multiplier, 1),
            "carbs": round(self.carbs_per_100g * multiplier, 1),
        }


FOOD_ANALYSIS_PROMPT = """Ты эксперт-нутрициолог. Проанализируй изображение еды и определи:
1. Название блюда на русском
2. Калории на 100г
3. Белки на 100г
4. Жиры на 100г
5. Углеводы на 100г

ВАЖНО: Ответ должен быть ТОЛЬКО в формате JSON без каких-либо пояснений!

Формат ответа:
{
    "food_name": "название блюда на русском",
    "food_name_en": "dish name in english",
    "calories_per_100g": 150,
    "protein_per_100g": 10,
    "fat_per_100g": 5,
    "carbs_per_100g": 15,
    "estimated_portion_grams": 200,
    "description": "краткое описание"
}

Если на изображении нет еды:
{"error": "no_food", "message": "На изображении не обнаружена еда"}"""

WEIGHT_OPTIONS = [50, 100, 150, 200, 250, 300, 400, 500]


class FoodRecognizer:
    """Класс для распознавания еды через Groq API (Llama 4 Scout)"""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Настройка прокси
        proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
        self.proxy = proxy if proxy else None

    def is_available(self) -> bool:
        """Проверить доступность API"""
        return bool(self.api_key)

    async def recognize_from_image(self, image_data: bytes) -> Tuple[bool, Optional[NutritionInfo], str]:
        """Распознать еду по фотографии через Groq (Llama 4 Scout)"""
        if not self.is_available():
            return False, None, "❌ Groq API недоступен. Проверьте GROQ_API_KEY."

        try:
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": FOOD_ANALYSIS_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }

            # Создаем сессию с прокси
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url, 
                    headers=headers, 
                    json=payload,
                    proxy=self.proxy
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Groq API error: {response.status} - {error_text}")
                        return False, None, f"❌ Ошибка API: {response.status}"

                    result = await response.json()

            if not result.get("choices"):
                return False, None, "❌ Пустой ответ от Groq."

            text = result["choices"][0]["message"]["content"].strip()

            if "```" in text:
                text = re.sub(r'^```\w*\n?', '', text)
                text = re.sub(r'\n?```$', '', text)

            json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if json_match:
                text = json_match.group(0)

            try:
                data = json.loads(text.strip())
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON: {e}")
                logger.error(f"Ответ: {text[:500]}")
                return False, None, "❌ Ошибка распознавания. Попробуйте ещё раз."

            if "error" in data:
                return False, None, f"❌ {data.get('message', 'Еда не обнаружена')}"

            nutrition = NutritionInfo(
                name=data.get("food_name", "Неизвестное блюдо"),
                name_en=data.get("food_name_en", "unknown"),
                calories_per_100g=float(data.get("calories_per_100g", 0)),
                protein_per_100g=float(data.get("protein_per_100g", 0)),
                fat_per_100g=float(data.get("fat_per_100g", 0)),
                carbs_per_100g=float(data.get("carbs_per_100g", 0)),
                portion_grams=float(data.get("estimated_portion_grams", 150)),
                confidence=0.9,
                description=data.get("description", "")
            )

            logger.info(f"Распознано: {nutrition.name}")
            return True, nutrition, "✅ Еда успешно распознана!"

        except Exception as e:
            logger.error(f"Ошибка распознавания: {e}")
            return False, None, f"❌ Ошибка: {str(e)}"

    @staticmethod
    def get_weight_options() -> List[int]:
        return WEIGHT_OPTIONS.copy()

    @staticmethod
    def calculate_nutrition(nutrition_info: NutritionInfo, weight_grams: float) -> Dict:
        return nutrition_info.calculate_for_weight(weight_grams)

    @staticmethod
    def format_nutrition_message(nutrition_info: NutritionInfo, weight_grams: float = None) -> str:
        if weight_grams is None:
            weight_grams = nutrition_info.portion_grams

        calculated = nutrition_info.calculate_for_weight(weight_grams)

        message = f"""🍽 *{nutrition_info.name}*
{f'_{nutrition_info.description}_' if nutrition_info.description else ''}

📊 *Пищевая ценность на 100г:*
🔥 Калории: *{nutrition_info.calories_per_100g:.0f} ккал*
🥩 Белки: *{nutrition_info.protein_per_100g:.1f} г*
🧈 Жиры: *{nutrition_info.fat_per_100g:.1f} г*
🍚 Углеводы: *{nutrition_info.carbs_per_100g:.1f} г*

⚖️ *Для порции {weight_grams:.0f}г:*
🔥 Калории: *{calculated['calories']} ккал*
🥩 Белки: *{calculated['protein']:.1f} г*
🧈 Жиры: *{calculated['fat']:.1f} г*
🍚 Углеводы: *{calculated['carbs']:.1f} г*"""

        return message


food_recognizer = FoodRecognizer()


async def recognize_food_image(image_data: bytes) -> Tuple[bool, Optional[Dict], str]:
    success, nutrition, message = await food_recognizer.recognize_from_image(image_data)

    if success and nutrition:
        return True, {
            "name": nutrition.name,
            "name_en": nutrition.name_en,
            "calories_per_100g": nutrition.calories_per_100g,
            "protein_per_100g": nutrition.protein_per_100g,
            "fat_per_100g": nutrition.fat_per_100g,
            "carbs_per_100g": nutrition.carbs_per_100g,
            "portion_grams": nutrition.portion_grams,
            "confidence": nutrition.confidence,
            "description": nutrition.description,
        }, message

    return False, None, message


def calculate_calories_for_weight(food_data: Dict, weight_grams: float) -> Dict:
    multiplier = weight_grams / 100.0
    return {
        "name": food_data.get("name", ""),
        "weight_grams": weight_grams,
        "calories": round(food_data.get("calories_per_100g", 0) * multiplier),
        "protein": round(food_data.get("protein_per_100g", 0) * multiplier, 1),
        "fat": round(food_data.get("fat_per_100g", 0) * multiplier, 1),
        "carbs": round(food_data.get("carbs_per_100g", 0) * multiplier, 1),
    }

"""
Food image analyzer using Google Gemini Vision API
Uses official google-generativeai library for reliable integration
"""
import os
import logging
import json
import re
import asyncio
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Check if Gemini is available
GEMINI_AVAILABLE = False
genai = None

try:
    import google.generativeai as genai_module
    genai = genai_module
    GEMINI_AVAILABLE = True
    logger.info("Google Generative AI library loaded successfully")
except ImportError:
    logger.warning("google-generativeai not installed, Gemini will not be available")

# System prompt for food analysis
FOOD_ANALYSIS_PROMPT = """Ты эксперт-нутрициолог. Проанализируй это изображение еды и верни JSON с информацией о блюде.

ВАЖНО: Ответ должен быть ТОЛЬКО валидным JSON без markdown, без ```json```, без пояснений!

Формат ответа:
{
    "food_name": "название блюда на русском",
    "food_name_en": "dish name in english", 
    "confidence": 0.95,
    "portion_grams": 250,
    "calories": 350,
    "protein": 25,
    "fat": 15,
    "carbs": 30,
    "description": "краткое описание блюда",
    "ingredients": ["ингредиент1", "ингредиент2"],
    "alternatives": [
        {"name": "альтернатива1", "calories": 300, "protein": 20, "fat": 12, "carbs": 25},
        {"name": "альтернатива2", "calories": 280, "protein": 18, "fat": 10, "carbs": 28}
    ]
}

Если на изображении нет еды, верни:
{"error": "no_food", "message": "На изображении не обнаружена еда"}

Оценивай калории и БЖУ на ВИДИМУЮ порцию (не на 100г)."""


def is_gemini_available() -> bool:
    """Check if Gemini API is available at runtime"""
    api_key = os.getenv("GEMINI_API_KEY", "")
    return GEMINI_AVAILABLE and bool(api_key)


def _configure_gemini():
    """Configure Gemini API with the API key"""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return False
    
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        logger.error(f"Failed to configure Gemini: {e}")
        return False


async def analyze_with_gemini(image_data: bytes) -> Optional[Dict]:
    """
    Analyze food image using Google Gemini Vision API
    
    Args:
        image_data: Image as bytes
        
    Returns:
        Dict with food analysis or None if failed
    """
    if not is_gemini_available():
        logger.warning("Gemini API not available")
        return None
    
    if not _configure_gemini():
        logger.warning("Failed to configure Gemini API")
        return None
    
    try:
        # Create model instance
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create image part
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_data
        }
        
        # Generate content in a thread pool
        def _generate():
            response = model.generate_content(
                [FOOD_ANALYSIS_PROMPT, image_part],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=1024,
                )
            )
            return response
        
        # Run synchronous call in executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _generate)
        
        if response and response.text:
            text = response.text.strip()
            
            # Clean up the response - remove markdown code blocks if present
            if text.startswith("```"):
                text = re.sub(r'^```\w*\n?', '', text)
                text = re.sub(r'\n?```$', '', text)
            
            try:
                food_data = json.loads(text.strip())
                logger.info(f"Gemini recognized: {food_data.get('food_name', 'unknown')}")
                return food_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Raw response: {text[:500]}")
                return None
        
        return None
        
    except Exception as e:
        logger.error(f"Gemini analysis error: {e}")
        return None


async def get_gemini_food_analysis(image_data: bytes) -> Dict:
    """
    Get comprehensive food analysis from Gemini
    
    Returns:
        Dict with success status and food data
    """
    result = await analyze_with_gemini(image_data)
    
    if result is None:
        return {
            "success": False,
            "source": "gemini",
            "message": "❌ Не удалось проанализировать изображение. Проверьте API ключ или попробуйте позже."
        }
    
    if "error" in result:
        return {
            "success": False,
            "source": "gemini",
            "message": f"❌ {result.get('message', 'Еда не обнаружена на изображении')}"
        }
    
    # Format successful response
    food_name = result.get("food_name", "Неизвестное блюдо")
    calories = result.get("calories", 0)
    protein = result.get("protein", 0)
    fat = result.get("fat", 0)
    carbs = result.get("carbs", 0)
    portion = result.get("portion_grams", 100)
    description = result.get("description", "")
    confidence = result.get("confidence", 0.9)
    
    message = f"""🤖 *Анализ с помощью ИИ*

🍽 *{food_name}*
{f'_{description}_' if description else ''}

📊 *Пищевая ценность* (порция ~{portion}г):

🔥 Калории: *{calories} ккал*
🥩 Белки: *{protein} г*
🧈 Жиры: *{fat} г*
🍚 Углеводы: *{carbs} г*

🎯 Уверенность: {int(confidence * 100)}%
"""
    
    # Add alternatives if present
    alternatives = result.get("alternatives", [])
    if alternatives:
        message += "\n📋 *Возможно это также:*\n"
        for alt in alternatives[:2]:
            message += f"• {alt.get('name', '')} ({alt.get('calories', 0)} ккал)\n"
    
    return {
        "success": True,
        "source": "gemini",
        "food_class": result.get("food_name_en", food_name).lower().replace(" ", "_"),
        "food_name": food_name,
        "confidence": confidence,
        "nutrition": {
            "name": food_name,
            "portion_grams": portion,
            "calories": calories,
            "protein": protein,
            "fat": fat,
            "carbs": carbs
        },
        "alternatives": alternatives,
        "message": message,
        "predictions": [{
            "food_class": result.get("food_name_en", food_name).lower().replace(" ", "_"),
            "name_ru": food_name,
            "confidence": confidence,
            "nutrition": {
                "name": food_name,
                "portion_grams": portion,
                "calories": calories,
                "protein": protein,
                "fat": fat,
                "carbs": carbs
            }
        }]
    }

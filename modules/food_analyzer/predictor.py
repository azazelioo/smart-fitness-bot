"""
Food analyzer predictor - Multi-source food recognition
Priority: Gemini AI > Hugging Face > Local model
"""
import os
import logging
from typing import Dict, List, Tuple
from .nutrition_db import get_food_info, calculate_portion_nutrition, format_nutrition_result

logger = logging.getLogger(__name__)

# Try to import AI analyzers
GEMINI_IMPORTED = False
try:
    from .gemini_analyzer import get_gemini_food_analysis
    GEMINI_IMPORTED = True
    logger.info("Gemini analyzer module imported")
except ImportError as e:
    logger.warning(f"Gemini analyzer not available: {e}")

# Hugging Face as fallback
HF_AVAILABLE = False
try:
    from .hf_classifier import get_food_prediction, get_top_food_predictions
    HF_AVAILABLE = True
    logger.info("HF classifier available as fallback (101 categories)")
except ImportError:
    logger.warning("HF classifier not available")

# Local model as last resort
LOCAL_AVAILABLE = False
try:
    from .model import classify_food_image, classify_food_image_top_k
    LOCAL_AVAILABLE = True
except ImportError:
    logger.warning("Local classifier not available")


def is_gemini_available() -> bool:
    """Check if Gemini API is available - checks at runtime, not import time"""
    api_key = os.getenv("GEMINI_API_KEY", "")
    available = GEMINI_IMPORTED and bool(api_key)
    if available:
        logger.debug(f"Gemini API available (key: {api_key[:10]}...)")
    return available


async def analyze_food_image(image_data: bytes) -> Dict:
    """
    Analyze food image and return nutritional information
    Uses Gemini AI for best results (unlimited food categories)
    
    Args:
        image_data: Image as bytes
        
    Returns:
        Dict with food analysis including calories and nutrition
    """
    
    # Priority 1: Google Gemini (best, unlimited categories) - CHECK AT RUNTIME
    if is_gemini_available():
        try:
            logger.info("Using Gemini AI for food analysis...")
            result = await get_gemini_food_analysis(image_data)
            if result.get("success"):
                logger.info(f"Gemini recognized: {result.get('food_name', 'unknown')}")
                return result
            else:
                logger.warning(f"Gemini failed: {result.get('message', 'unknown error')}")
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
    else:
        logger.info("Gemini not available, using fallback...")
    
    # Priority 2: Hugging Face (101 Food categories)
    if HF_AVAILABLE:
        try:
            result = await get_food_prediction(image_data)
            if result:
                food_class, confidence, name_ru = result
                logger.info(f"HF recognized: {food_class} ({confidence:.2%})")
                
                food_info = get_food_info(food_class)
                if food_info:
                    nutrition = calculate_portion_nutrition(food_info)
                    return {
                        "success": True,
                        "source": "huggingface",
                        "food_class": food_class,
                        "confidence": confidence,
                        "food_info": food_info,
                        "nutrition": nutrition,
                        "message": format_nutrition_result(food_class, nutrition)
                    }
        except Exception as e:
            logger.error(f"HF prediction failed: {e}")
    
    # Priority 3: Local model
    if LOCAL_AVAILABLE:
        try:
            food_class, confidence = await classify_food_image(image_data)
            logger.info(f"Local model recognized: {food_class}")
            
            food_info = get_food_info(food_class)
            if food_info:
                nutrition = calculate_portion_nutrition(food_info)
                return {
                    "success": True,
                    "source": "local",
                    "food_class": food_class,
                    "confidence": confidence,
                    "food_info": food_info,
                    "nutrition": nutrition,
                    "message": format_nutrition_result(food_class, nutrition)
                }
        except Exception as e:
            logger.error(f"Local prediction failed: {e}")
    
    return {
        "success": False,
        "message": "❌ Не удалось распознать блюдо. Убедитесь что:\n• На фото видна еда\n• Хорошее освещение\n• Фото не размытое"
    }


async def analyze_food_image_with_alternatives(image_data: bytes, k: int = 3) -> Dict:
    """
    Analyze food image and return predictions with alternatives
    Uses multi-source recognition for best results
    """
    
    # Priority 1: Gemini AI (best quality, any food) - CHECK AT RUNTIME
    if is_gemini_available():
        try:
            logger.info("Using Gemini AI for food analysis with alternatives...")
            result = await get_gemini_food_analysis(image_data)
            if result.get("success"):
                logger.info(f"Gemini analysis successful: {result.get('food_name')}")
                return result
            else:
                logger.warning(f"Gemini returned error: {result.get('message')}")
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
    else:
        logger.info("Gemini not available, falling back to HF...")
    
    # Priority 2: Hugging Face (101 categories)
    predictions = []
    if HF_AVAILABLE:
        try:
            hf_predictions = await get_top_food_predictions(image_data, k)
            if hf_predictions:
                predictions = [(p[0], p[1]) for p in hf_predictions]
                logger.info(f"HF top predictions: {[(p[0], f'{p[1]:.2%}') for p in predictions]}")
        except Exception as e:
            logger.error(f"HF top-k prediction failed: {e}")
    
    # Priority 3: Local model
    if not predictions and LOCAL_AVAILABLE:
        try:
            predictions = await classify_food_image_top_k(image_data, k)
        except Exception as e:
            logger.error(f"Local top-k prediction failed: {e}")
    
    if not predictions:
        return {
            "success": False,
            "predictions": [],
            "message": "❌ Не удалось распознать блюдо. Попробуйте:\n• Сфотографировать сверху\n• Улучшить освещение\n• Приблизить камеру к еде"
        }
    
    # Build results from predictions
    results = []
    for food_class, confidence in predictions:
        food_info = get_food_info(food_class)
        if food_info:
            nutrition = calculate_portion_nutrition(food_info)
            results.append({
                "food_class": food_class,
                "name_ru": food_info.get("name_ru", food_class.replace("_", " ").title()),
                "confidence": confidence,
                "nutrition": nutrition
            })
    
    if results:
        message = "🍽 *Результаты анализа:*\n\n"
        
        for i, r in enumerate(results):
            emoji = "🥇" if i == 0 else ("🥈" if i == 1 else "🥉")
            conf_pct = round(r["confidence"] * 100, 1)
            message += f"{emoji} *{r['name_ru']}* ({conf_pct}%)\n"
            message += f"   ├ 🔥 {r['nutrition']['calories']} ккал\n"
            message += f"   ├ 🥩 Б: {r['nutrition']['protein']}г\n"
            message += f"   ├ 🧈 Ж: {r['nutrition']['fat']}г\n"
            message += f"   └ 🍚 У: {r['nutrition']['carbs']}г\n\n"
        
        message += "_Нажмите на кнопку, чтобы добавить в дневник_"
        
        return {
            "success": True,
            "source": "huggingface",
            "predictions": results,
            "message": message
        }
    
    return {
        "success": False,
        "predictions": [{"food_class": p[0], "confidence": p[1]} for p in predictions],
        "message": f"🔍 Возможно это: {', '.join([p[0].replace('_', ' ').title() for p in predictions[:3]])}\n\n❌ Информация о КБЖУ для этих блюд не найдена в базе."
    }


def get_available_sources() -> List[str]:
    """Get list of available recognition sources"""
    sources = []
    if is_gemini_available():
        sources.append("gemini")
    if HF_AVAILABLE:
        sources.append("huggingface")
    if LOCAL_AVAILABLE:
        sources.append("local")
    return sources

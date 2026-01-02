"""
Food image classifier using Hugging Face Inference API
Uses fine-tuned ViT model on Food-101 dataset
"""
import os
import logging
import aiohttp
import base64
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

# Hugging Face API settings
HF_API_URL = "https://api-inference.huggingface.co/models/nateraw/food"
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")  # Optional, works without token but with rate limits

# Food-101 class names with Russian translations
FOOD_TRANSLATIONS = {
    "apple_pie": "Яблочный пирог",
    "baby_back_ribs": "Рёбрышки барбекю",
    "baklava": "Пахлава",
    "beef_carpaccio": "Карпаччо из говядины",
    "beef_tartare": "Тартар из говядины",
    "beet_salad": "Свекольный салат",
    "beignets": "Бенье (пончики)",
    "bibimbap": "Бибимбап",
    "bread_pudding": "Хлебный пудинг",
    "breakfast_burrito": "Буррито на завтрак",
    "bruschetta": "Брускетта",
    "caesar_salad": "Салат Цезарь",
    "cannoli": "Канноли",
    "caprese_salad": "Салат Капрезе",
    "carrot_cake": "Морковный торт",
    "ceviche": "Севиче",
    "cheese_plate": "Сырная тарелка",
    "cheesecake": "Чизкейк",
    "chicken_curry": "Куриное карри",
    "chicken_quesadilla": "Кесадилья с курицей",
    "chicken_wings": "Куриные крылышки",
    "chocolate_cake": "Шоколадный торт",
    "chocolate_mousse": "Шоколадный мусс",
    "churros": "Чуррос",
    "clam_chowder": "Похлёбка из моллюсков",
    "club_sandwich": "Клаб-сэндвич",
    "crab_cakes": "Крабовые котлеты",
    "creme_brulee": "Крем-брюле",
    "croque_madame": "Крок-мадам",
    "cup_cakes": "Капкейки",
    "deviled_eggs": "Фаршированные яйца",
    "donuts": "Пончики",
    "dumplings": "Пельмени/Дамплинги",
    "edamame": "Эдамаме",
    "eggs_benedict": "Яйца Бенедикт",
    "escargots": "Эскарго (улитки)",
    "falafel": "Фалафель",
    "filet_mignon": "Филе-миньон",
    "fish_and_chips": "Рыба с картошкой фри",
    "foie_gras": "Фуа-гра",
    "french_fries": "Картошка фри",
    "french_onion_soup": "Французский луковый суп",
    "french_toast": "Французские тосты",
    "fried_calamari": "Жареные кальмары",
    "fried_rice": "Жареный рис",
    "frozen_yogurt": "Замороженный йогурт",
    "garlic_bread": "Чесночный хлеб",
    "gnocchi": "Ньокки",
    "greek_salad": "Греческий салат",
    "grilled_cheese_sandwich": "Горячий сэндвич с сыром",
    "grilled_salmon": "Лосось на гриле",
    "guacamole": "Гуакамоле",
    "gyoza": "Гёдза",
    "hamburger": "Гамбургер",
    "hot_and_sour_soup": "Кисло-острый суп",
    "hot_dog": "Хот-дог",
    "huevos_rancheros": "Уэвос ранчерос",
    "hummus": "Хумус",
    "ice_cream": "Мороженое",
    "lasagna": "Лазанья",
    "lobster_bisque": "Суп-биск из лобстера",
    "lobster_roll_sandwich": "Ролл с лобстером",
    "macaroni_and_cheese": "Макароны с сыром",
    "macarons": "Макаронс",
    "miso_soup": "Мисо суп",
    "mussels": "Мидии",
    "nachos": "Начос",
    "omelette": "Омлет",
    "onion_rings": "Луковые кольца",
    "oysters": "Устрицы",
    "pad_thai": "Пад тай",
    "paella": "Паэлья",
    "pancakes": "Блинчики/Панкейки",
    "panna_cotta": "Панна котта",
    "peking_duck": "Утка по-пекински",
    "pho": "Фо (вьетнамский суп)",
    "pizza": "Пицца",
    "pork_chop": "Свиная отбивная",
    "poutine": "Путин (картошка с соусом)",
    "prime_rib": "Рёберная часть говядины",
    "pulled_pork_sandwich": "Сэндвич с рваной свининой",
    "ramen": "Рамен",
    "ravioli": "Равиоли",
    "red_velvet_cake": "Торт Красный бархат",
    "risotto": "Ризотто",
    "samosa": "Самоса",
    "sashimi": "Сашими",
    "scallops": "Морские гребешки",
    "seaweed_salad": "Салат из водорослей",
    "shrimp_and_grits": "Креветки с кашей",
    "spaghetti_bolognese": "Спагетти болоньезе",
    "spaghetti_carbonara": "Спагетти карбонара",
    "spring_rolls": "Спринг-роллы",
    "steak": "Стейк",
    "strawberry_shortcake": "Клубничный торт",
    "sushi": "Суши",
    "tacos": "Такос",
    "takoyaki": "Такояки",
    "tiramisu": "Тирамису",
    "tuna_tartare": "Тартар из тунца",
    "waffles": "Вафли"
}


async def classify_with_huggingface(image_data: bytes) -> List[Tuple[str, float, str]]:
    """
    Classify food image using Hugging Face Inference API
    
    Returns:
        List of (english_name, confidence, russian_name) tuples
    """
    headers = {}
    if HF_API_TOKEN:
        headers["Authorization"] = f"Bearer {HF_API_TOKEN}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                HF_API_URL,
                headers=headers,
                data=image_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    results = await response.json()
                    
                    # Parse results
                    predictions = []
                    for item in results[:5]:  # Top 5
                        label = item.get("label", "").lower().replace(" ", "_")
                        score = item.get("score", 0)
                        ru_name = FOOD_TRANSLATIONS.get(label, label.replace("_", " ").title())
                        predictions.append((label, score, ru_name))
                    
                    return predictions
                    
                elif response.status == 503:
                    logger.warning("HF model is loading, will retry...")
                    return []
                else:
                    error_text = await response.text()
                    logger.error(f"HF API error {response.status}: {error_text}")
                    return []
                    
    except Exception as e:
        logger.error(f"HF classification error: {e}")
        return []


async def get_food_prediction(image_data: bytes) -> Optional[Tuple[str, float, str]]:
    """
    Get the top food prediction
    
    Returns:
        Tuple of (english_name, confidence, russian_name) or None
    """
    predictions = await classify_with_huggingface(image_data)
    
    if predictions:
        return predictions[0]
    
    return None


async def get_top_food_predictions(image_data: bytes, k: int = 3) -> List[Tuple[str, float, str]]:
    """
    Get top-k food predictions
    
    Returns:
        List of (english_name, confidence, russian_name) tuples
    """
    predictions = await classify_with_huggingface(image_data)
    return predictions[:k]

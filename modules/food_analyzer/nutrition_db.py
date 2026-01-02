"""
Food nutrition database - Extended version with 10,000+ items
Contains nutritional information for foods that can be recognized
"""
import json
from pathlib import Path
from typing import Optional, Dict, List

# Load the extended database
DATABASE_PATH = Path(__file__).parent / "food_database.json"

# In-memory cache
_database_cache: Optional[Dict] = None


def load_database() -> Dict:
    """Load food database from JSON file"""
    global _database_cache
    
    if _database_cache is not None:
        return _database_cache
    
    if DATABASE_PATH.exists():
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            _database_cache = json.load(f)
            print(f"Loaded {len(_database_cache)} food items from database")
            return _database_cache
    
    # Fallback to basic database if JSON not found
    _database_cache = FALLBACK_DATABASE
    return _database_cache


# Fallback database for basic functionality
FALLBACK_DATABASE = {
    "pizza": {"name_ru": "Пицца", "calories": 266, "protein": 11, "fat": 10, "carbs": 33, "portion": 200},
    "hamburger": {"name_ru": "Гамбургер", "calories": 295, "protein": 17, "fat": 14, "carbs": 24, "portion": 200},
    "sushi": {"name_ru": "Суши", "calories": 140, "protein": 5, "fat": 2, "carbs": 26, "portion": 200},
    "salad": {"name_ru": "Салат", "calories": 85, "protein": 4, "fat": 5, "carbs": 7, "portion": 200},
    "steak": {"name_ru": "Стейк", "calories": 271, "protein": 26, "fat": 18, "carbs": 0, "portion": 250},
    "pasta": {"name_ru": "Паста", "calories": 160, "protein": 6, "fat": 4, "carbs": 28, "portion": 300},
    "chicken_curry": {"name_ru": "Курица карри", "calories": 130, "protein": 15, "fat": 5, "carbs": 6, "portion": 300},
    "fried_rice": {"name_ru": "Жареный рис", "calories": 163, "protein": 4, "fat": 5, "carbs": 25, "portion": 250},
    "pancakes": {"name_ru": "Блины", "calories": 227, "protein": 6, "fat": 9, "carbs": 31, "portion": 150},
    "omelette": {"name_ru": "Омлет", "calories": 154, "protein": 11, "fat": 12, "carbs": 1, "portion": 150},
    "borsch": {"name_ru": "Борщ", "calories": 49, "protein": 2, "fat": 2, "carbs": 6, "portion": 300},
    "pelmeni": {"name_ru": "Пельмени", "calories": 275, "protein": 13, "fat": 14, "carbs": 25, "portion": 200},
    "caesar_salad": {"name_ru": "Салат Цезарь", "calories": 127, "protein": 7, "fat": 9, "carbs": 5, "portion": 250},
    "cheesecake": {"name_ru": "Чизкейк", "calories": 321, "protein": 6, "fat": 23, "carbs": 24, "portion": 125},
    "grilled_salmon": {"name_ru": "Лосось на гриле", "calories": 208, "protein": 25, "fat": 12, "carbs": 0, "portion": 180},
}


def get_food_info(food_class: str) -> Optional[Dict]:
    """Get nutritional information for a food class"""
    db = load_database()
    
    # Try exact match first
    food = db.get(food_class.lower())
    if food:
        return food
    
    # Try with underscores replaced
    food = db.get(food_class.lower().replace(" ", "_"))
    if food:
        return food
    
    # Try partial match
    for key, value in db.items():
        if food_class.lower() in key.lower():
            return value
        name_ru = value.get("name_ru", "").lower()
        if food_class.lower() in name_ru:
            return value
    
    return None


def calculate_portion_nutrition(food_info: Dict, portion_grams: float = None) -> Dict:
    """Calculate nutrition for a specific portion size"""
    if portion_grams is None:
        portion_grams = food_info.get("portion", 100)
    
    multiplier = portion_grams / 100
    
    return {
        "name": food_info.get("name_ru", ""),
        "portion_grams": portion_grams,
        "calories": round(food_info["calories"] * multiplier),
        "protein": round(food_info["protein"] * multiplier, 1),
        "fat": round(food_info["fat"] * multiplier, 1),
        "carbs": round(food_info["carbs"] * multiplier, 1)
    }


def format_nutrition_result(food_class: str, nutrition: Dict) -> str:
    """Format nutrition result as readable message"""
    return f"""
🍽 *{nutrition['name']}*

📊 *Пищевая ценность* (порция ~{nutrition['portion_grams']}г):

🔥 Калории: *{nutrition['calories']} ккал*
🥩 Белки: *{nutrition['protein']} г*
🧈 Жиры: *{nutrition['fat']} г*
🍚 Углеводы: *{nutrition['carbs']} г*

💡 _Данные приблизительные, основаны на стандартной порции_
"""


def search_food_by_name(query: str, limit: int = 10) -> List[Dict]:
    """Search foods by Russian name"""
    db = load_database()
    results = []
    query_lower = query.lower()
    
    for key, value in db.items():
        name_ru = value.get("name_ru", "").lower()
        if query_lower in name_ru or query_lower in key:
            results.append({
                "key": key,
                **value
            })
            if len(results) >= limit:
                break
    
    return results


def get_foods_by_category(category: str, limit: int = 50) -> List[Dict]:
    """Get foods by category"""
    db = load_database()
    results = []
    
    for key, value in db.items():
        if value.get("category") == category:
            results.append({"key": key, **value})
            if len(results) >= limit:
                break
    
    return results


def get_all_categories() -> List[str]:
    """Get list of all categories"""
    db = load_database()
    categories = set()
    
    for value in db.values():
        cat = value.get("category")
        if cat:
            categories.add(cat)
    
    return sorted(list(categories))


def get_database_stats() -> Dict:
    """Get database statistics"""
    db = load_database()
    categories = {}
    
    for value in db.values():
        cat = value.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total_items": len(db),
        "categories": categories
    }

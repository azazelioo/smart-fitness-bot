from .model import FastFoodClassifier, classify_food_image, classify_food_image_top_k, FOOD_CLASSES
from .nutrition_db import get_food_info, calculate_portion_nutrition, format_nutrition_result, search_food_by_name
from .predictor import analyze_food_image, analyze_food_image_with_alternatives
from .food_recognizer import (
    FoodRecognizer, 
    NutritionInfo, 
    food_recognizer,
    recognize_food_image,
    calculate_calories_for_weight,
    WEIGHT_OPTIONS
)

# Alias for backward compatibility
FoodClassifier = FastFoodClassifier

__all__ = [
    "FoodClassifier",
    "FastFoodClassifier",
    "classify_food_image",
    "classify_food_image_top_k",
    "FOOD_CLASSES",
    "get_food_info",
    "calculate_portion_nutrition",
    "format_nutrition_result",
    "search_food_by_name",
    "analyze_food_image",
    "analyze_food_image_with_alternatives",
    # Новые экспорты
    "FoodRecognizer",
    "NutritionInfo",
    "food_recognizer",
    "recognize_food_image",
    "calculate_calories_for_weight",
    "WEIGHT_OPTIONS"
]


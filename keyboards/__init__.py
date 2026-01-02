"""Keyboards package for SmartFit Coach Bot"""

from .inline import (
    get_main_menu_keyboard,
    get_pain_location_keyboard,
    get_pain_type_keyboard,
    get_pain_duration_keyboard,
    get_pain_intensity_keyboard,
    get_after_analysis_keyboard,
)

__all__ = [
    "get_main_menu_keyboard",
    "get_pain_location_keyboard",
    "get_pain_type_keyboard",
    "get_pain_duration_keyboard",
    "get_pain_intensity_keyboard",
    "get_after_analysis_keyboard",
]

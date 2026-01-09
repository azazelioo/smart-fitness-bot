from .start import router as start_router
from .registration import router as registration_router
from .training import router as training_router
from .nutrition import router as nutrition_router
from .profile import router as profile_router

__all__ = [
    "start_router",
    "registration_router", 
    "training_router",
    "nutrition_router",
    "profile_router",
]

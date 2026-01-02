"""
CRUD operations for database
"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, WorkoutPlan, FoodItem, FoodLog, WeightLog


# ============== User Operations ==============

async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    """Get user by Telegram ID"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, telegram_id: int, username: str = None, first_name: str = None) -> User:
    """Create new user"""
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, user: User, **kwargs) -> User:
    """Update user fields"""
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    user.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(user)
    return user


# ============== Workout Plan Operations ==============

async def create_workout_plan(session: AsyncSession, user_id: int, name: str, plan_data: dict) -> WorkoutPlan:
    """Create workout plan for user"""
    # Deactivate previous plans
    result = await session.execute(
        select(WorkoutPlan).where(
            and_(WorkoutPlan.user_id == user_id, WorkoutPlan.is_active == True)
        )
    )
    for old_plan in result.scalars():
        old_plan.is_active = False
    
    plan = WorkoutPlan(
        user_id=user_id,
        name=name,
        plan_data=plan_data
    )
    session.add(plan)
    await session.commit()
    await session.refresh(plan)
    return plan


async def get_active_workout_plan(session: AsyncSession, user_id: int) -> Optional[WorkoutPlan]:
    """Get user's active workout plan"""
    result = await session.execute(
        select(WorkoutPlan).where(
            and_(WorkoutPlan.user_id == user_id, WorkoutPlan.is_active == True)
        )
    )
    return result.scalar_one_or_none()


# ============== Food Operations ==============

async def get_food_item_by_name(session: AsyncSession, name: str) -> Optional[FoodItem]:
    """Get food item by name (case-insensitive)"""
    result = await session.execute(
        select(FoodItem).where(FoodItem.name.ilike(f"%{name}%"))
    )
    return result.scalar_one_or_none()


async def create_food_log(
    session: AsyncSession,
    user_id: int,
    food_name: str,
    calories: float,
    protein: float,
    fat: float,
    carbs: float,
    portion_grams: float = 100.0,
    food_item_id: int = None,
    meal_type: str = None
) -> FoodLog:
    """Log food entry for user"""
    log = FoodLog(
        user_id=user_id,
        food_item_id=food_item_id,
        food_name=food_name,
        portion_grams=portion_grams,
        calories=calories,
        protein=protein,
        fat=fat,
        carbs=carbs,
        meal_type=meal_type
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


async def get_today_food_logs(session: AsyncSession, user_id: int) -> List[FoodLog]:
    """Get today's food logs for user"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(FoodLog).where(
            and_(
                FoodLog.user_id == user_id,
                FoodLog.logged_at >= today_start
            )
        ).order_by(FoodLog.logged_at)
    )
    return list(result.scalars())


async def get_daily_totals(session: AsyncSession, user_id: int) -> dict:
    """Get today's nutrition totals"""
    logs = await get_today_food_logs(session, user_id)
    return {
        "calories": sum(log.calories for log in logs),
        "protein": sum(log.protein for log in logs),
        "fat": sum(log.fat for log in logs),
        "carbs": sum(log.carbs for log in logs),
        "meals_count": len(logs)
    }


# ============== Weight Log Operations ==============

async def create_weight_log(session: AsyncSession, user_id: int, weight: float) -> WeightLog:
    """Log weight entry"""
    log = WeightLog(user_id=user_id, weight=weight)
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


async def get_weight_history(session: AsyncSession, user_id: int, days: int = 30) -> List[WeightLog]:
    """Get weight history for last N days"""
    since = datetime.utcnow() - timedelta(days=days)
    result = await session.execute(
        select(WeightLog).where(
            and_(
                WeightLog.user_id == user_id,
                WeightLog.logged_at >= since
            )
        ).order_by(WeightLog.logged_at)
    )
    return list(result.scalars())

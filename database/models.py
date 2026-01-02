"""
Database models for Smart Fitness Assistant
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, BigInteger, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """User profile model"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Anthropometry
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # male/female
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # cm
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # kg
    
    # Preferences
    activity_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    goal: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # lose/maintain/gain
    training_location: Mapped[Optional[str]] = mapped_column(String(20), default="home")  # home/gym
    experience_level: Mapped[Optional[str]] = mapped_column(String(20), default="beginner")
    
    # Calculated values
    bmr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tdee: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Registration state
    registration_step: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_registered: Mapped[bool] = mapped_column(default=False)
    
    # Relationships
    workout_plans: Mapped[list["WorkoutPlan"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    food_logs: Mapped[list["FoodLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    weight_logs: Mapped[list["WeightLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class WorkoutPlan(Base):
    """Workout plan model"""
    __tablename__ = "workout_plans"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plan_data: Mapped[dict] = mapped_column(JSON)  # Full plan structure
    
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="workout_plans")


class FoodItem(Base):
    """Food/dish reference model"""
    __tablename__ = "food_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    name_ru: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Nutrition per 100g
    calories: Mapped[float] = mapped_column(Float)
    protein: Mapped[float] = mapped_column(Float)
    fat: Mapped[float] = mapped_column(Float)
    carbs: Mapped[float] = mapped_column(Float)
    
    # Standard portion size in grams
    portion_size: Mapped[float] = mapped_column(Float, default=100.0)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class FoodLog(Base):
    """User food log entry"""
    __tablename__ = "food_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    food_item_id: Mapped[Optional[int]] = mapped_column(ForeignKey("food_items.id"), nullable=True)
    
    food_name: Mapped[str] = mapped_column(String(200))
    portion_grams: Mapped[float] = mapped_column(Float, default=100.0)
    
    # Calculated for portion
    calories: Mapped[float] = mapped_column(Float)
    protein: Mapped[float] = mapped_column(Float)
    fat: Mapped[float] = mapped_column(Float)
    carbs: Mapped[float] = mapped_column(Float)
    
    meal_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # breakfast/lunch/dinner/snack
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="food_logs")


class WeightLog(Base):
    """User weight tracking"""
    __tablename__ = "weight_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    weight: Mapped[float] = mapped_column(Float)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="weight_logs")

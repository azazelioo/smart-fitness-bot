"""
Smart Fitness Bot - Unified Version
Combines injury assessment, food recognition, training, and KBJU calculator
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import config
from database import init_db

# Import all handlers
from bot.handlers import (
    start_router,
    registration_router,
    training_router,
    nutrition_router,
    profile_router,
    assessment_router,
    advice_router
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Webhook settings
WEBHOOK_PATH = "/webhook"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 10000))


async def on_startup(bot: Bot):
    """Actions on startup - initialize DB and set webhook"""
    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
    
    # Set webhook for Render deployment
    render_url = os.getenv("RENDER_EXTERNAL_URL", "")
    
    if render_url:
        webhook_url = f"{render_url}{WEBHOOK_PATH}"
        await bot.set_webhook(webhook_url, drop_pending_updates=True)
        logger.info(f"✅ Webhook set: {webhook_url}")
    else:
        logger.warning("⚠️  RENDER_EXTERNAL_URL not set, webhook not configured")
        logger.info("Starting in polling mode for local development")


async def on_shutdown(bot: Bot):
    """Actions on shutdown"""
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("🛑 Bot stopped")


async def health_check(request):
    """Health check endpoint for Render"""
    return web.Response(text="OK", status=200)


def main():
    """Main function to run the bot"""
    
    # Check for bot token
    if not config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
        return
    
    # Create bot with default parse_mode
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    # Create dispatcher with memory storage for FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register routers
    logger.info("📝 Registering handlers...")
    
    # Core handlers from smart-fitness-bot
    dp.include_router(start_router)
    dp.include_router(registration_router)
    dp.include_router(nutrition_router)
    dp.include_router(training_router)
    dp.include_router(profile_router)
    
    # Additional handlers from smart-fit-bot
    dp.include_router(assessment_router)
    dp.include_router(advice_router)
    
    logger.info("   ✅ All handlers registered successfully")
    
    # Register startup/shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Bot info
    logger.info("=" * 60)
    logger.info("🤖 Smart Fitness Bot v3.0 - Unified Edition")
    logger.info("=" * 60)
    logger.info("Features:")
    logger.info("   ✅ 🍽 Food Recognition (AI-powered)")
    logger.info("   ✅ 🤕 Injury Assessment")
    logger.info("   ✅ 💪 Training Generation")
    logger.info("   ✅ 📊 KBJU Calculator")
    logger.info(f"   📍 Port: {WEBAPP_PORT}")
    logger.info("=" * 60)
    
    # Create web application
    app = web.Application()
    
    # Setup health check endpoint  
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    
    # Setup webhook handler
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    
    # Setup application
    setup_application(app, dp, bot=bot)
    
    # Run server
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Received stop signal")
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        raise

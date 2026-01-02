"""
Database connection and session management
Supports SQLite (local) and PostgreSQL (cloud)
"""
import logging
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from .models import Base
from config import config

logger = logging.getLogger(__name__)

# Get DATABASE_URL and ensure correct async driver
database_url = config.DATABASE_URL

# Fix URL to use async driver
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info("Converted to asyncpg driver")
elif database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    logger.info("Converted postgres:// to asyncpg driver")

# Determine database type
is_postgres = "postgresql" in database_url

# Engine configuration
engine_kwargs = {
    "echo": False,
}

if is_postgres:
    # PostgreSQL cloud configuration with SSL
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["poolclass"] = NullPool
    
    # SSL configuration for Supabase
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Disable prepared statement caching for pgBouncer/Supavisor
    # This is required for Supabase Transaction Pooler
    engine_kwargs["connect_args"] = {
        "ssl": ssl_context,
        "prepared_statement_cache_size": 0,  # Disable asyncpg prepared statements
        "statement_cache_size": 0,  # Disable asyncpg statement cache
        "command_timeout": 60,
        "server_settings": {
            "application_name": "smart_fitness_bot"
        }
    }
    
    # Additional execution options to disable prepared statements at SQLAlchemy level
    engine_kwargs["execution_options"] = {
        "no_parameters": True,
    }
    
    logger.info("Configured for PostgreSQL (cloud) with SSL, no prepared statements")
else:
    logger.info("Configured for SQLite (local)")

logger.info(f"Database URL scheme: {database_url.split('://')[0] if '://' in database_url else 'unknown'}")

engine = create_async_engine(database_url, **engine_kwargs)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize database tables"""
    logger.info("Initializing database...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        error_str = str(e)
        # If prepared statement error occurs, tables likely already exist
        if "prepared statement" in error_str.lower() or "DuplicatePreparedStatement" in error_str:
            logger.warning("Prepared statement conflict - tables likely already exist in Supabase")
            logger.info("Continuing with existing tables...")
        else:
            logger.error(f"Database initialization error: {e}")
            raise


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session() as session:
        yield session


async def test_connection():
    """Test database connection"""
    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

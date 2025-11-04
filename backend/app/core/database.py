from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from .config import settings
from app.base import Base

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=True,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Seed default data
async def seed_default_data():
    """Seed default LLM models (optional - users should add models via LLM Settings page)"""
    from app.models import LLMModel

    async with AsyncSessionLocal() as session:
        try:
            # Check if we already have models
            result = await session.execute(select(LLMModel))
            existing_models = result.scalars().all()

            if existing_models:
                print("Default data already seeded, skipping...")
                return

            print("No default models configured. Users should add models via LLM Settings page.")

        except Exception as e:
            print(f"Error checking default data: {e}")
            await session.rollback()


# Initialize database
async def init_db():
    # Run migrations first to handle existing databases
    from app.utils.migrations import migrate_schema
    try:
        await migrate_schema(engine)
    except Exception as e:
        print(f"Migration warning: {e}")
        # Continue even if migration has issues
    
    # Create all tables (for new databases or new tables)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default data
    await seed_default_data()


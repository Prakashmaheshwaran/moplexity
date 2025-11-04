from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import select
from app.config import settings
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
    """Seed default LLM providers and models"""
    from app.models import LLMProvider, LLMModel

    async with AsyncSessionLocal() as session:
        try:
            # Check if we already have providers
            result = await session.execute(select(LLMProvider))
            existing_providers = result.scalars().all()

            if existing_providers:
                print("Default data already seeded, skipping...")
                return

            print("Seeding default LLM providers and models...")

            # Default providers
            providers_data = [
                {
                    "name": "OpenAI",
                    "provider_type": "openai",
                    "api_key": "",  # Empty - user needs to configure
                    "is_active": True
                },
                {
                    "name": "Anthropic",
                    "provider_type": "anthropic",
                    "api_key": "",  # Empty - user needs to configure
                    "is_active": True
                },
                {
                    "name": "Google AI",
                    "provider_type": "gemini",
                    "api_key": "",  # Empty - user needs to configure
                    "is_active": True
                }
            ]

            providers = []
            for provider_data in providers_data:
                provider = LLMProvider(**provider_data)
                session.add(provider)
                providers.append(provider)

            await session.commit()

            # Refresh providers to get IDs
            for provider in providers:
                await session.refresh(provider)

            # Note: Models are not pre-configured. Users should add models via LLM Settings page.
            # This allows users to configure only the models they want to use.

            await session.commit()
            print("Default providers seeded successfully! (No models pre-configured)")

        except Exception as e:
            print(f"Error seeding default data: {e}")
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


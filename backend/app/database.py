from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import select
from app.config import settings
from app.models import LLMProvider, LLMModel

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

# Base class for models
Base = declarative_base()


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

            # Default models
            models_data = [
                # OpenAI models
                {
                    "provider_id": providers[0].id,
                    "model_name": "gpt-3.5-turbo",
                    "display_name": "GPT-3.5 Turbo",
                    "description": "Fast and cost-effective model for most tasks",
                    "is_active": True
                },
                {
                    "provider_id": providers[0].id,
                    "model_name": "gpt-4",
                    "display_name": "GPT-4",
                    "description": "Most capable GPT model for complex reasoning",
                    "is_active": True
                },
                {
                    "provider_id": providers[0].id,
                    "model_name": "gpt-4-turbo",
                    "display_name": "GPT-4 Turbo",
                    "description": "Latest GPT-4 model with improved performance",
                    "is_active": True
                },

                # Anthropic models
                {
                    "provider_id": providers[1].id,
                    "model_name": "claude-3-sonnet-20240229",
                    "display_name": "Claude 3 Sonnet",
                    "description": "Balanced model for most use cases",
                    "is_active": True
                },
                {
                    "provider_id": providers[1].id,
                    "model_name": "claude-3-opus-20240229",
                    "display_name": "Claude 3 Opus",
                    "description": "Most powerful Claude model for complex tasks",
                    "is_active": True
                },

                # Google models
                {
                    "provider_id": providers[2].id,
                    "model_name": "gemini/gemini-2.0-flash",
                    "display_name": "Gemini 2.0 Flash",
                    "description": "Fast and efficient multimodal model",
                    "is_active": True
                },
                {
                    "provider_id": providers[2].id,
                    "model_name": "gemini/gemini-pro",
                    "display_name": "Gemini Pro",
                    "description": "Advanced multimodal model for complex tasks",
                    "is_active": True
                }
            ]

            for model_data in models_data:
                model = LLMModel(**model_data)
                session.add(model)

            await session.commit()
            print("Default data seeded successfully!")

        except Exception as e:
            print(f"Error seeding default data: {e}")
            await session.rollback()


# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default data
    await seed_default_data()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import chat, search, conversations, llm_config, suggestions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    await init_db()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Moplexity API",
    description="Perplexity-like AI search and chat API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(llm_config.router, prefix="/api/llm", tags=["llm-config"])
app.include_router(suggestions.router, prefix="/api/chat", tags=["chat"])


@app.get("/")
async def root():
    return {"message": "Moplexity API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


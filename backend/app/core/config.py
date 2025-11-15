from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # LLM configuration is managed via database models

    # Search API Keys (Optional)
    bing_search_api_key: Optional[str] = None
    google_search_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None

    # Database
    database_url: str = "sqlite+aiosqlite:///./moplexity.db"

    # Server Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"
    debug: bool = False
    cors_origins: Optional[str] = None
    admin_token: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


settings = Settings()


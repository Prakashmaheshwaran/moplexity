from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # LiteLLM Configuration
    litellm_model: str = "gpt-3.5-turbo"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


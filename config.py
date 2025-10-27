from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # WhatsApp Configuration
    whatsapp_phone_number_id: str
    whatsapp_business_account_id: str
    whatsapp_access_token: str
    whatsapp_verify_token: str

    # SerpAPI Configuration
    serpapi_api_key: str

    # Anthropic Configuration
    anthropic_api_key: str

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

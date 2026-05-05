from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "CityLunch API"
    DATABASE_URL: str = "sqlite:///./citylunch.db"

    # JWT — REMPLACER en production via la variable d'environnement JWT_SECRET_KEY
    JWT_SECRET_KEY: str = "change-me-please-use-a-real-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24h

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
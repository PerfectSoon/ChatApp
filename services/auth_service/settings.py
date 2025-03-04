from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    service_name: str = "auth_service"
    service_description: str = "Authentication microservice"
    database_url: str = "sqlite:///./database.db"
    secret_key: str = 'SUPER_SECRET_KEY'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 1800

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )

settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    service_name: str = "chat_service"
    service_description: str = "Chat microservice"
    database_url: str = "sqlite+aiosqlite:///./chat.db"
    secret_key: str = 'SUPER_SECRET_KEY'
    algorithm: str = 'HS256'


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )

settings = Settings()

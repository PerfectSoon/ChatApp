from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    service_name: str = "chat_service"
    service_description: str = "Chat microservice"
    database_url: str = "postgresql+asyncpg://user2:password2@postgres_service2:5432/chat_db"
    secret_key: str
    algorithm: str


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )

settings = Settings()

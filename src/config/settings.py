from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    ASYNC_DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    EXCHANGE_API_KEY: str
    GEMINI_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

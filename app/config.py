from pydantic_settings import BaseSettings,SettingsConfigDict


class Settings(BaseSettings):
    API_KEY: str
    DATABASE_NAME: str
    DATABASE_PORT: int
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()



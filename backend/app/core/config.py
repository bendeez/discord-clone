from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

class FirebaseConfig(BaseModel):
    apiKey: str
    authDomain: str
    databaseURL: str
    projectId: str
    storageBucket: str
    messagingSenderId: str
    appId: str
    measurementId: str
class Settings(BaseSettings):
    FIREBASE_CONFIG: FirebaseConfig
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    DATABASE_NAME: str
    DATABASE_PORT: int
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

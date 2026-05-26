import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Personal Expense Tracker API"
    MONGODB_URL: str = "mongodb://localhost:27017/expense_db"
    JWT_SECRET_KEY: str = "SuperSecretRandom32ByteHashOrGenerateUsingOpenssl"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

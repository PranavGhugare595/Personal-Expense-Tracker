import os
from pydantic_settings import BaseSettings
from typing import Optional, Any

class Settings(BaseSettings):
    PROJECT_NAME: str = "Personal Expense Tracker API"
    MONGODB_URL: str = "mongodb://localhost:27017/expense_db"
    JWT_SECRET_KEY: str = "SuperSecretRandom32ByteHashOrGenerateUsingOpenssl"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: Any = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://personal-expense-tracker-frontend.vercel.app"
    ]

    # Email reminder settings
    SMTP_EMAIL: Optional[str] = None           # Your Gmail address e.g. you@gmail.com
    SMTP_APP_PASSWORD: Optional[str] = None    # Gmail App Password (16-char)
    REMINDER_HOUR: int = 21                    # Hour to send reminder (24h, IST). Default = 9 PM
    REMINDER_MINUTE: int = 0                   # Minute offset within the hour

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()


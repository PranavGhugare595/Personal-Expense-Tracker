import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    # JWT Configuration
    JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret-key")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "1440"))

    # App Config
    APP_NAME = os.getenv("APP_NAME", "AI Expense Tracker API")
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Email SMTP Configuration
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    REMINDER_ENABLED = os.getenv("REMINDER_ENABLED", "true").lower() in ("true", "1", "t")

settings = Config()

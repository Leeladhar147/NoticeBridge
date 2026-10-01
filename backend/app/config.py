import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env if present
load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "NoticeBridge")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api/v1")
    
    # PostgreSQL as the primary database with SQLAlchemy 2.0
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://noticebridge:noticebridge_dev_secret@localhost:5439/noticebridge"
    )
    
    # JWT Authentication settings
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "noticebridge_jwt_dev_secret_key_replace_in_production_2026"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,*"
        ).split(",")
        if origin.strip()
    ]
    SIMULATION_MODE: bool = os.getenv("FINANCIAL_SIMULATION_MODE", os.getenv("SIMULATION_MODE", "true")).lower() in ("true", "1", "yes")
    FINANCIAL_SIMULATION_MODE: bool = os.getenv("FINANCIAL_SIMULATION_MODE", os.getenv("SIMULATION_MODE", "true")).lower() in ("true", "1", "yes")
    LEGAL_DISCLAIMER: str = (
        "NoticeBridge is a notice-period transition and financing simulation prototype. "
        "All calculations are hypothetical financing simulations and estimated buyout models. "
        "It does NOT provide actual lending, guaranteed financing, credit approval, real money transfer, "
        "or legal/financial advice. All results depend on contractual terms and user inputs."
    )

settings = Settings()

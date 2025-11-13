import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "smart-tourist-safety")
    ENV: str = os.getenv("ENV", "dev")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change_me")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@db:5432/safety")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    POLYGON_RPC_URL: str = os.getenv("POLYGON_RPC_URL", "https://rpc-amoy.polygon.technology")
    CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "")
    ALLOW_ORIGINS: str = os.getenv("ALLOW_ORIGINS", "*")

settings = Settings()

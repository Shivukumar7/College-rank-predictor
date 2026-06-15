from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ExamRank AI API"
    DEBUG: bool = True
    CORS_ORIGINS: list = ["http://localhost:3000"]
    DATA_PATH: str = "app/data"
    
    class Config:
        env_file = ".env"

settings = Settings()

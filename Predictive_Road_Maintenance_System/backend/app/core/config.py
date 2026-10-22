import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "RoadPredict AI — Component 4 Research Engine"
    PROJECT_ID: str = "J26-IT-336"
    VERSION: str = "4.8.0"
    API_V1_STR: str = "/api"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    DATA_PROCESSED: str = os.path.join(BASE_DIR, "data", "processed")
    MODELS_DIR: str = os.path.join(BASE_DIR, "models")
    EXPERIMENTS_DIR: str = os.path.join(BASE_DIR, "experiments")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'data', 'road_maintenance.db')}")
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

settings = Settings()

os.makedirs(settings.MODELS_DIR, exist_ok=True)
os.makedirs(settings.EXPERIMENTS_DIR, exist_ok=True)
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.DATA_PROCESSED, exist_ok=True)

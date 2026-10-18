"""
main.py
-------
FastAPI REST API Server for Component 4: AI-Based Predictive Road Maintenance.
Project ID: J26-IT-336
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.core.config import settings
from backend.app.models.database import init_db
from backend.app.services.database_seeder import seed_database
from backend.app.ml.models import model_service

# Routers
from backend.app.routers.dashboard import router as dashboard_router
from backend.app.routers.roads import router as roads_router
from backend.app.routers.predict import router as predict_router
from backend.app.routers.models import router as models_router
from backend.app.routers.maintenance import router as maintenance_router
from backend.app.routers.datasets import router as datasets_router
from backend.app.routers.integration import router as integration_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB and models
    print(f"[{settings.PROJECT_NAME}] Starting API server v{settings.VERSION}...")
    init_db()
    try:
        seed_database(force=False)
    except Exception as e:
        print(f"Warning: Database seeding notice: {e}")
        
    print(f"[{settings.PROJECT_NAME}] Model Engine Status: Ready={model_service.is_loaded}")
    yield
    print(f"[{settings.PROJECT_NAME}] Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Component 4: AI-Based Predictive Road Maintenance Research API (SLIIT J26-IT-336)",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(roads_router, prefix=settings.API_V1_STR)
app.include_router(predict_router, prefix=settings.API_V1_STR)
app.include_router(models_router, prefix=settings.API_V1_STR)
app.include_router(maintenance_router, prefix=settings.API_V1_STR)
app.include_router(datasets_router, prefix=settings.API_V1_STR)
app.include_router(integration_router, prefix=settings.API_V1_STR)

@app.get("/api/health", tags=["Health"])
def health_check():
    """System health check and engine readiness."""
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "project_id": settings.PROJECT_ID,
        "version": settings.VERSION,
        "models_loaded": model_service.is_loaded,
        "environment": settings.ENVIRONMENT,
        "database": "SQLite (Connected)"
    }

@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

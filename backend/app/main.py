import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.ml.predictor import predictor
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-Ready Personal Expense Tracker with Machine Learning Insights",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 endpoints router
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["General"])
def read_root():
    return {
        "message": "Welcome to the Personal Expense Tracker ML Engine REST API Gateway.",
        "docs_url": "/docs",
        "health": "healthy",
        "environment": settings.ENVIRONMENT
    }

@app.get("/health", tags=["General"])
def health_check():
    return {
        "status": "healthy",
        "model_loaded": predictor.model is not None,
        "database": "MongoDB" if not os.path.exists("mock_database.json") else "JSON_Offline_Fallback"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

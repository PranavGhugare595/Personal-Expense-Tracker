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
origins = [
    "http://localhost:5173", # Vite React standard development port
    "http://localhost:3000",
    "https://personal-expense-tracker-frontend.vercel.app" # Production frontend URL placeholder
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

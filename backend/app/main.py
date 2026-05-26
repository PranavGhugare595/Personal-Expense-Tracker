import os
import json
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
raw_origins = settings.CORS_ORIGINS
origins = []

if isinstance(raw_origins, str):
    # Try parsing as JSON array (e.g. '["*"]' or '["http://localhost:5173"]')
    try:
        parsed = json.loads(raw_origins)
        if isinstance(parsed, list):
            origins = [str(item).strip() for item in parsed]
        elif isinstance(parsed, str):
            origins = [parsed.strip()]
    except Exception:
        # If not valid JSON, treat it as a comma-separated list of strings
        origins = [orig.strip() for orig in raw_origins.split(",") if orig.strip()]
elif isinstance(raw_origins, list):
    origins = [str(orig).strip() for orig in raw_origins]
else:
    origins = ["*"] # Safe fallback

# Ensure standard local development ports are always whitelisted
if "http://localhost:5173" not in origins and "*" not in origins:
    origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 endpoints router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    try:
        from app.core.database import db_manager
        users = db_manager.find_many("users", {})
        if not users:
            print("[INFO] Database empty on startup! Automatic seeding triggered...")
            import sys
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(backend_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            from seed_db import seed_data
            seed_data()
            print("[INFO] Database automatic seeding complete.")
        else:
            print(f"[INFO] Database contains {len(users)} users. Skipping auto-seeding.")
    except Exception as e:
        print(f"[WARNING] Database auto-seeding on startup failed: {e}")

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

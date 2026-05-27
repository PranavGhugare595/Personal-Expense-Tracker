import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.v1.router import api_router
from app.ml.predictor import predictor
from app.core.config import settings
from app.core.scheduler import start_scheduler, stop_scheduler

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

    # Start the daily expense reminder scheduler
    try:
        start_scheduler()
    except Exception as e:
        print(f"[WARNING] Failed to start reminder scheduler: {e}")


@app.on_event("shutdown")
def shutdown_event():
    try:
        stop_scheduler()
    except Exception as e:
        print(f"[WARNING] Failed to stop reminder scheduler cleanly: {e}")

@app.get("/", response_class=HTMLResponse, tags=["General"])
def read_root():
    # Read the root index.html file from the project root directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    index_path = os.path.join(backend_dir, "index.html")
    if os.path.exists(index_path):
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=200)
        except Exception as e:
            return HTMLResponse(content=f"<h3>Error loading index.html: {e}</h3>", status_code=500)
    return HTMLResponse(content="<h3>Error: index.html not found in project root directory!</h3>", status_code=404)

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

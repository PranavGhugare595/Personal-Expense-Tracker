from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.expenses import router as expenses_router
from app.api.v1.endpoints.profile import router as profile_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — connect to Supabase PostgreSQL on startup, close on shutdown."""
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="AI Expense Tracker API",
    description="Backend API for the AI-powered personal expense tracker with ML budget forecasting.",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# ──── CORS Middleware ────
# Allow frontend dev server and production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:5174",   # Vite dev server alternate
        "http://localhost:3000",   # Alternate dev port
        "http://127.0.0.1:5173",
        settings.FRONTEND_URL      # Configured frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──── API Routers ────
app.include_router(auth_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(expenses_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint — health check."""
    return {
        "app": "AI Expense Tracker API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

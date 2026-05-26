from fastapi import APIRouter

from app.api.v1.endpoints import auth, expenses, budgets, ml_features

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
api_router.include_router(ml_features.router, prefix="/ml", tags=["Machine Learning"])

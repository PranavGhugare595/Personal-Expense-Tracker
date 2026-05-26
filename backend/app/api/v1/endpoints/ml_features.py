from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Any, Dict, List
from app.api.deps import get_current_user
from app.core.database import db_manager
from app.ml.predictor import predictor
from app.ml.forecaster import FinanceForecaster

router = APIRouter()

class CategorySuggestionRequest(BaseModel):
    description: str

class CategorySuggestionResponse(BaseModel):
    suggested_category: str
    confidence: float
    is_suggested: bool

@router.post("/suggest-category", response_model=CategorySuggestionResponse)
def suggest_category(
    request: CategorySuggestionRequest,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    ML Prediction Endpoint.
    Analyzes transaction text to suggest the most matching budget category.
    """
    try:
        if not request.description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction description string cannot be empty"
            )
        
        category, confidence = predictor.predict(request.description)
        return {
            "suggested_category": category,
            "confidence": confidence,
            "is_suggested": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NLP inference layer failure: {str(e)}"
        )

@router.get("/forecast")
def get_expense_forecast(current_user: dict = Depends(get_current_user)) -> Any:
    """
    Time-Series Expense Forecasting.
    Uses historical expense data points to forecast cumulative spending over the next 3 months.
    """
    try:
        query = {"userId": current_user["_id"]}
        expenses = db_manager.find_many("expenses", query)
        
        # Standardize representation for pandas parser
        cleaned_expenses = []
        for exp in expenses:
            cleaned_expenses.append({
                "amount": float(exp["amount"]),
                "date": exp["date"] if isinstance(exp["date"], str) else exp["date"].isoformat()
            })
            
        projections = FinanceForecaster.forecast_next_months(cleaned_expenses)
        return {"forecasts": projections}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecasting engine failed: {str(e)}"
        )

@router.get("/insights")
def get_ml_spending_insights(
    income: float = 4000.0,
    safety_allocation: float = 20.0,
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Spending Pattern Analysis & Smart Category Recommendations.
    Generates personalized targets by auditing spending ratios under custom user ratios.
    """
    try:
        query = {"userId": current_user["_id"]}
        expenses = db_manager.find_many("expenses", query)
        
        cleaned_expenses = []
        for exp in expenses:
            cleaned_expenses.append({
                "amount": float(exp["amount"]),
                "category": exp["category"],
                "date": exp["date"] if isinstance(exp["date"], str) else exp["date"].isoformat()
            })
            
        recommendations = FinanceForecaster.generate_budget_recommendations(
            cleaned_expenses, 
            monthly_income=income, 
            savings_ratio=safety_allocation / 100.0
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Insight engine failed: {str(e)}"
        )


@router.post("/retrain", status_code=status.HTTP_200_OK)
def force_category_retraining(current_user: dict = Depends(get_current_user)) -> Any:
    """
    Active Classifier Optimization.
    Trains the localized text vectorizer using updated actual expense logs to adapt to custom user labels.
    """
    query = {"userId": current_user["_id"]}
    expenses = db_manager.find_many("expenses", query)
    
    if len(expenses) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 8 logged expenses are required to fit a custom classification model."
        )
        
    descriptions = [exp["description"] for exp in expenses]
    categories = [exp["category"] for exp in expenses]
    
    success = predictor.retrain_model(descriptions, categories)
    if success:
        return {"message": "Classifier retrained and updated successfully."}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Retraining pipeline failed during matrix operations."
        )

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any

class FinanceForecaster:
    @staticmethod
    def forecast_next_months(expenses: List[Dict[str, Any]], months_to_forecast: int = 3) -> List[Dict[str, Any]]:
        """
        Calculates spending predictions for the upcoming months.
        Uses linear regression and historical rolling averages with fallback safety layers.
        """
        if not expenses or len(expenses) < 3:
            # Fallback for empty or low-transaction accounts: return mock baseline projections
            current_date = datetime.utcnow()
            forecasts = []
            for i in range(1, months_to_forecast + 1):
                next_month = current_date + timedelta(days=30 * i)
                forecasts.append({
                    "month": next_month.strftime("%Y-%m"),
                    "predicted_amount": 1200.0 + (i * 50.0), # Standard placeholder projection
                    "confidence_interval": [1000.0, 1400.0],
                    "status": "bootstrap_default"
                })
            return forecasts

        try:
            # Load into pandas DataFrame
            df = pd.DataFrame(expenses)
            # Standardize date and amount
            df["date"] = pd.to_datetime(df["date"])
            df["amount"] = df["amount"].astype(float)
            
            # Resample by month
            df_monthly = df.set_index("date").resample("ME")["amount"].sum().reset_index()
            
            # Convert to numeric dates
            df_monthly["month_index"] = np.arange(len(df_monthly))
            
            X = df_monthly["month_index"].values
            y = df_monthly["amount"].values
            
            if len(df_monthly) >= 2:
                # Calculate simple linear regression coefficients
                slope, intercept = np.polyfit(X, y, 1)
            else:
                # If only one month data, project flat slope
                slope = 0.0
                intercept = y[0]

            last_month_idx = len(df_monthly) - 1
            current_date = df["date"].max()
            forecasts = []

            for i in range(1, months_to_forecast + 1):
                proj_idx = last_month_idx + i
                predicted_val = float(max(100.0, slope * proj_idx + intercept)) # Don't predict negative spending
                
                # Standard deviation calculation for confidence interval bounds
                std_dev = float(np.std(y)) if len(y) > 1 else predicted_val * 0.15
                margin = max(50.0, std_dev * 1.96)
                
                next_month = current_date + timedelta(days=30 * i)
                forecasts.append({
                    "month": next_month.strftime("%Y-%m"),
                    "predicted_amount": round(predicted_val, 2),
                    "confidence_interval": [
                        round(max(0.0, predicted_val - margin), 2),
                        round(predicted_val + margin, 2)
                    ],
                    "status": "statistical_projection"
                })
            return forecasts
        except Exception as e:
            print(f"[WARNING] Forecasting error: {e}. Falling back to flat averages.")
            avg_spending = sum(e["amount"] for e in expenses) / max(1, len(expenses))
            current_date = datetime.utcnow()
            forecasts = []
            for i in range(1, months_to_forecast + 1):
                next_month = current_date + timedelta(days=30 * i)
                forecasts.append({
                    "month": next_month.strftime("%Y-%m"),
                    "predicted_amount": round(avg_spending * 4.0, 2), # Projected monthly flat average
                    "confidence_interval": [round(avg_spending * 3.0, 2), round(avg_spending * 5.0, 2)],
                    "status": "averaging_fallback"
                })
            return forecasts

    @staticmethod
    def generate_budget_recommendations(
        expenses: List[Dict[str, Any]], 
        monthly_income: float = 4000.0,
        savings_ratio: float = 0.20
    ) -> Dict[str, Any]:
        """
        Generates healthy budget bounds per category by blending active spending ratios with the 50/30/20 rule.
        """
        # Set base target allocations by dynamically scaling needs and wants in 5:3 ratio over remaining income
        remaining_ratio = 1.0 - savings_ratio
        needs_ratio = remaining_ratio * (5.0 / 8.0)
        wants_ratio = remaining_ratio * (3.0 / 8.0)

        needs_cap = monthly_income * needs_ratio  # Utilities, Rent, Health
        wants_cap = monthly_income * wants_ratio  # Food, Entertainment, Shopping
        savings_cap = monthly_income * savings_ratio # Target savings target


        if not expenses:
            return {
                "income": monthly_income,
                "recommended_savings": savings_cap,
                "recommended_limits": {
                    "Housing": needs_cap * 0.60,
                    "Utilities": needs_cap * 0.25,
                    "Health & Wellness": needs_cap * 0.15,
                    "Food & Dining": wants_cap * 0.40,
                    "Shopping": wants_cap * 0.30,
                    "Entertainment": wants_cap * 0.20,
                    "Transport": wants_cap * 0.10
                },
                "status": "unmodified_standards"
            }

        try:
            df = pd.DataFrame(expenses)
            df["amount"] = df["amount"].astype(float)
            
            # Aggregate category spending
            cat_totals = df.groupby("category")["amount"].sum().to_dict()
            total_spent = sum(cat_totals.values())
            
            # Map historical categories to needs vs wants classification
            needs_list = ["Housing", "Utilities", "Health & Wellness"]
            
            rec_limits = {}
            for cat, amount in cat_totals.items():
                ratio = amount / max(1.0, total_spent)
                if cat in needs_list:
                    # Allocate portion of needs cap, bounded by maximums
                    rec_limits[cat] = round(min(needs_cap * 0.70, max(150.0, needs_cap * ratio)), 2)
                else:
                    # Allocate portion of wants cap, bounded by maximums
                    rec_limits[cat] = round(min(wants_cap * 0.60, max(100.0, wants_cap * ratio)), 2)
            
            # Fill missing core standard categories
            all_standards = ["Housing", "Utilities", "Health & Wellness", "Food & Dining", "Shopping", "Entertainment", "Transport"]
            for s in all_standards:
                if s not in rec_limits:
                    if s in needs_list:
                        rec_limits[s] = round(needs_cap * 0.15, 2)
                    else:
                        rec_limits[s] = round(wants_cap * 0.15, 2)

            return {
                "income": monthly_income,
                "recommended_savings": round(max(savings_cap, monthly_income - total_spent), 2),
                "recommended_limits": rec_limits,
                "status": "optimized_user_ratio"
            }
        except Exception as e:
            print(f"[ERROR] Recommendation calculation failed: {e}")
            return {
                "income": monthly_income,
                "recommended_savings": savings_cap,
                "recommended_limits": {
                    "Food & Dining": wants_cap * 0.4,
                    "Transport": wants_cap * 0.2,
                    "Utilities": needs_cap * 0.3
                },
                "status": "fallback_error"
            }

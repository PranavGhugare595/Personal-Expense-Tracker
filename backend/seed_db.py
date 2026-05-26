import sys
import os
from datetime import datetime

# Ensure backend directory is in path for relative app imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from app.core.database import db_manager
from app.core.security import get_password_hash

def serialize_dates(doc):
    """Recursively converts python datetime objects to ISO strings for JSON storage."""
    serialized = {}
    for k, v in doc.items():
        if isinstance(v, datetime):
            # Ensure it ends with 'Z' for ISO UTC compatibility
            serialized[k] = v.isoformat() + "Z"
        elif isinstance(v, dict):
            serialized[k] = serialize_dates(v)
        elif isinstance(v, list):
            serialized[k] = [serialize_dates(x) if isinstance(x, dict) else x for x in v]
        else:
            serialized[k] = v
    return serialized

def clear_database():
    print("[Seeder] Cleaning existing database collections...")
    if not db_manager.is_fallback:
        db_manager.db["users"].drop()
        db_manager.db["expenses"].drop()
        db_manager.db["budgets"].drop()
        print("[Seeder] MongoDB collections dropped.")
    else:
        db_manager.mock_db = {
            "users": {},
            "expenses": {},
            "budgets": {}
        }
        db_manager.save_mock_data()
        print("[Seeder] Offline JSON database cleared.")

def seed_data():
    print("[Seeder] Starting database seeding...")
    
    # 1. Create Default Test User
    password_hash = get_password_hash("password123")
    user_doc = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "currency": "USD",
        "password_hash": password_hash,
        "created_at": datetime(2026, 2, 1, 9, 0, 0),
        "updated_at": datetime(2026, 2, 1, 9, 0, 0)
    }
    
    if db_manager.is_fallback:
        user_doc = serialize_dates(user_doc)
        
    user_id = db_manager.insert_one("users", user_doc)
    print(f"[Seeder] Created test user: jane@example.com (ID: {user_id})")
    
    # 2. Seed 4 Months of Expenses (Feb, Mar, Apr, May 2026)
    # Total monthly limits are around $2500, with income around $4000.
    # Jane has realistic expenses under: Housing, Utilities, Food & Dining, Transport, Entertainment, Shopping.
    expenses = []
    
    months = [
        (2, 28, 2026), # February
        (3, 31, 2026), # March
        (4, 30, 2026), # April
        (5, 26, 2026), # May (up to May 26 today)
    ]
    
    for month_num, max_days, year in months:
        # Housing Rent
        expenses.append({
            "userId": user_id,
            "amount": 1200.0,
            "description": "Monthly rent payment apartment lease",
            "category": "Housing",
            "date": datetime(year, month_num, 1, 10, 0, 0),
            "payment_method": "Bank Transfer",
            "ml_metadata": {
                "is_suggested": False,
                "confidence_score": 1.0,
                "original_description": "Monthly rent payment apartment lease"
            }
        })
        
        # Utilities (Electricity)
        expenses.append({
            "userId": user_id,
            "amount": 110.0 + (month_num * 5.0), 
            "description": "Electricity utility bill monthly heating",
            "category": "Utilities",
            "date": datetime(year, month_num, 14, 11, 30, 0),
            "payment_method": "Credit Card",
            "ml_metadata": {
                "is_suggested": True,
                "confidence_score": 0.92,
                "original_description": "Electricity utility bill monthly heating"
            }
        })
        
        # Utilities (Wifi Router)
        expenses.append({
            "userId": user_id,
            "amount": 79.99,
            "description": "High speed home wifi router broad",
            "category": "Utilities",
            "date": datetime(year, month_num, 15, 9, 0, 0),
            "payment_method": "Credit Card",
            "ml_metadata": {
                "is_suggested": True,
                "confidence_score": 0.94,
                "original_description": "High speed home wifi router broad"
            }
        })

        # Utilities (Water)
        expenses.append({
            "userId": user_id,
            "amount": 35.0 + (month_num * 2.0),
            "description": "Water utility clean supply bill",
            "category": "Utilities",
            "date": datetime(year, month_num, 16, 14, 0, 0),
            "payment_method": "Credit Card",
            "ml_metadata": {
                "is_suggested": True,
                "confidence_score": 0.91,
                "original_description": "Water utility clean supply bill"
            }
        })
        
        # Weekly items (Groceries, Coffee, Transport, Fuel)
        grocery_days = [7, 14, 21, 28] if max_days >= 28 else [6, 13, 20, 27]
        for idx, day in enumerate(grocery_days):
            # Only seed if day is in the past for May
            if year == 2026 and month_num == 5 and day > 26:
                continue
                
            # Groceries
            expenses.append({
                "userId": user_id,
                "amount": 125.50 + (idx * 8.0) - (month_num * 2.0),
                "description": "grocery supermarket items food organic",
                "category": "Food & Dining",
                "date": datetime(year, month_num, day, 12, 0, 0),
                "payment_method": "Debit Card",
                "ml_metadata": {
                    "is_suggested": True,
                    "confidence_score": 0.96,
                    "original_description": "grocery supermarket items food organic"
                }
            })
            
            # Starbucks Coffee
            expenses.append({
                "userId": user_id,
                "amount": 12.40 + (idx * 1.50),
                "description": "starbucks latte coffee morning",
                "category": "Food & Dining",
                "date": datetime(year, month_num, day - 2, 8, 30, 0),
                "payment_method": "Apple Pay",
                "ml_metadata": {
                    "is_suggested": True,
                    "confidence_score": 0.98,
                    "original_description": "starbucks latte coffee morning"
                }
            })
            
            # Transport (Uber)
            expenses.append({
                "userId": user_id,
                "amount": 22.0 + (idx * 3.50) + (month_num * 1.0),
                "description": "uber ride city airport cab",
                "category": "Transport",
                "date": datetime(year, month_num, day - 1, 18, 45, 0),
                "payment_method": "Credit Card",
                "ml_metadata": {
                    "is_suggested": True,
                    "confidence_score": 0.95,
                    "original_description": "uber ride city airport cab"
                }
            })

            # Transport (Fuel)
            expenses.append({
                "userId": user_id,
                "amount": 42.50 + (idx * 2.0),
                "description": "shell gas station fuel fill tank",
                "category": "Transport",
                "date": datetime(year, month_num, day - 4, 15, 20, 0),
                "payment_method": "Credit Card",
                "ml_metadata": {
                    "is_suggested": True,
                    "confidence_score": 0.96,
                    "original_description": "shell gas station fuel fill tank"
                }
            })
            
        # Monthly Entertainment Subscription
        expenses.append({
            "userId": user_id,
            "amount": 19.99,
            "description": "netflix monthly hd plan subscription",
            "category": "Entertainment",
            "date": datetime(year, month_num, 5, 6, 0, 0),
            "payment_method": "Credit Card",
            "ml_metadata": {
                "is_suggested": True,
                "confidence_score": 0.97,
                "original_description": "netflix monthly hd plan subscription"
            }
        })
        
        # Cinema / Games
        if month_num >= 3:
            expenses.append({
                "userId": user_id,
                "amount": 35.0 if month_num == 3 else 55.0,
                "description": "cinema movie tickets popcorn" if month_num == 3 else "steam games digital console play",
                "category": "Entertainment",
                "date": datetime(year, month_num, 18, 20, 15, 0),
                "payment_method": "Debit Card",
                "ml_metadata": {
                    "is_suggested": True,
                    "confidence_score": 0.93,
                    "original_description": "cinema movie tickets popcorn" if month_num == 3 else "steam games digital console play"
                }
            })
            
        # Shopping / Clothes
        if month_num >= 4:
            expenses.append({
                "userId": user_id,
                "amount": 89.50 if month_num == 4 else 124.99,
                "description": "target department retail store malls" if month_num == 4 else "amazon delivery clothes shoes checkout online",
                "category": "Shopping",
                "date": datetime(year, month_num, 23, 16, 0, 0),
                "payment_method": "Credit Card",
                "ml_metadata": {
                    "is_suggested": True,
                    "confidence_score": 0.95,
                    "original_description": "target department retail store malls" if month_num == 4 else "amazon delivery clothes shoes checkout online"
                }
            })

    # Insert expenses into db
    for exp in expenses:
        if db_manager.is_fallback:
            exp = serialize_dates(exp)
        db_manager.insert_one("expenses", exp)
    print(f"[Seeder] Successfully seeded {len(expenses)} expense documents.")
    
    # 3. Create Budget Configuration for May 2026
    budget_doc = {
        "userId": user_id,
        "month": "2026-05",
        "total_limit": 2500.0,
        "category_limits": {
            "Housing": 1300.0,
            "Food & Dining": 600.0,
            "Transport": 250.0,
            "Utilities": 350.0
        },
        "ml_recommended": {
            "was_recommended": True,
            "recommended_savings_rate": 0.20
        },
        "created_at": datetime(2026, 5, 1, 0, 0, 0)
    }
    
    if db_manager.is_fallback:
        budget_doc = serialize_dates(budget_doc)
        
    budget_id = db_manager.insert_one("budgets", budget_doc)
    print(f"[Seeder] Created baseline active budget config for 2026-05 (ID: {budget_id})")
    
    print("[Seeder] Database seeding successfully completed!")

if __name__ == "__main__":
    clear_database()
    seed_data()

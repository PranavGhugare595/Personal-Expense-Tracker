from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timedelta
import io
import csv

from app.core.database import get_db
from app.models.sql_models import Expense
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/csv")
async def get_csv_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = select(Expense).where(Expense.user_id == current_user.id)
    
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.where(Expense.date >= start_dt)
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.where(Expense.date <= end_dt)
        
    query = query.order_by(Expense.date.desc())
    
    result = await db.execute(query)
    expenses = result.scalars().all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Description", "Category", "Payment Method", "Amount"])
    
    for exp in expenses:
        writer.writerow([
            exp.date.strftime("%Y-%m-%d %H:%M:%S"),
            exp.description,
            exp.category,
            exp.payment_route,
            f"{exp.amount:.2f}"
        ])
        
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=expense_report_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

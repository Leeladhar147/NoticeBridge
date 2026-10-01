from datetime import date, timedelta
from typing import Union

def format_inr(amount: Union[int, float]) -> str:
    """Format numbers into Indian Rupee style string (e.g. ₹1,20,000.00)."""
    return f"₹{amount:,.2f}"

def add_business_days(start_date: date, num_days: int) -> date:
    """Add business days (Monday-Friday) to a given start date."""
    current = start_date
    added = 0
    while added < num_days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Mon to Fri
            added += 1
    return current

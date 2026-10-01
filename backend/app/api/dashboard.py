from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.entities import User
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import DashboardService
from app.services.auth_service import get_current_user_flexible

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Returns user-specific transition summary and deterministic engine metrics.
    Enforces user data isolation.
    """
    return DashboardService.get_summary(db=db, user=current_user)

from datetime import datetime
from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": settings.SIMULATION_MODE,
        "financial_simulation_mode": settings.FINANCIAL_SIMULATION_MODE,
        "engines_active": [
            "NoticePeriodCalculator",
            "BuyoutCalculator",
            "JoiningDateCalculator",
            "RepaymentCalculator",
            "ScenarioEngine"
        ],
        "disclaimer": settings.LEGAL_DISCLAIMER
    }

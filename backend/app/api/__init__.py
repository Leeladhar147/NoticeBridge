from fastapi import APIRouter
from .health import router as health_router
from .employment import router as employment_router
from .calculators import router as calculators_router
from .dashboard import router as dashboard_router
from .auth import router as auth_router
from .documents import router as documents_router
from .affordability import router as affordability_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(employment_router)
api_router.include_router(calculators_router)
api_router.include_router(dashboard_router)
api_router.include_router(documents_router)
api_router.include_router(affordability_router)

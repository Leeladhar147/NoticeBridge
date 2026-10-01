from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.database import engine, Base
from app.api import api_router

# Ensure tables exist
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Deterministic Notice-Period Transition and Financing Simulation Platform",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes at root, /api, and /api/v1
app.include_router(api_router)
app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "description": "Notice-period transition and financing simulation platform",
        "version": settings.VERSION,
        "simulation_mode": True,
        "financial_simulation_mode": True,
        "documentation": "/docs",
        "disclaimer": settings.LEGAL_DISCLAIMER
    }

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "type": "ValueError"}
    )

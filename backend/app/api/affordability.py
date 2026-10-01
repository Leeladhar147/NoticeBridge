"""
Affordability Simulation API Router.
Provides deterministic calculation of disposable income and repayment percentages.
Enforces neutral, factual statements with zero credit approvals or underwriting decisions.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.intelligence import (
    AffordabilitySimulationRequest,
    AffordabilitySimulationResponse,
)
from app.engines.affordability_engine import AffordabilityCalculator

router = APIRouter(prefix="/affordability", tags=["Affordability Simulation"])


@router.post("/simulate", response_model=AffordabilitySimulationResponse)
def simulate_affordability(payload: AffordabilitySimulationRequest):
    """
    Hypothetical Affordability Simulation.
    Calculates:
    - repayment as percentage of entered monthly income
    - remaining income after entered obligations
    - remaining income after simulated repayment
    Strictly factual, non-judgmental wording without credit approval labels.
    """
    try:
        result = AffordabilityCalculator.calculate(
            new_monthly_income=payload.new_monthly_income,
            existing_monthly_obligations=payload.existing_monthly_obligations,
            simulated_monthly_repayment=payload.simulated_monthly_repayment,
        )
        return AffordabilitySimulationResponse(
            new_monthly_income=result.new_monthly_income,
            existing_monthly_obligations=result.existing_monthly_obligations,
            simulated_monthly_repayment=result.simulated_monthly_repayment,
            repayment_income_ratio_percent=result.repayment_income_ratio_percent,
            obligations_income_ratio_percent=result.obligations_income_ratio_percent,
            remaining_income_after_obligations=result.remaining_income_after_obligations,
            remaining_income_after_repayment=result.remaining_income_after_repayment,
            factual_summary=result.factual_summary,
            status_tone=result.status_tone,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

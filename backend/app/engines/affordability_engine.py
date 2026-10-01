"""
NoticeBridge Affordability Simulation Engine.
Deterministic calculation of disposable income and repayment percentages.
Per architectural requirements:
- Strictly factual, neutral wording
- Zero credit decisions or eligibility classification
- Clear mathematical formulas and provenance
"""

from typing import Dict, Any
from pydantic import BaseModel, Field
from app.schemas.origin import DataOrigin, TaggedValue


class AffordabilityResult(BaseModel):
    new_monthly_income: TaggedValue[float]
    existing_monthly_obligations: TaggedValue[float]
    simulated_monthly_repayment: TaggedValue[float]
    repayment_income_ratio_percent: TaggedValue[float]
    obligations_income_ratio_percent: TaggedValue[float]
    remaining_income_after_obligations: TaggedValue[float]
    remaining_income_after_repayment: TaggedValue[float]
    factual_summary: str
    status_tone: str  # "healthy", "moderate", "high_commitment"
    breakdown_steps: list[str]


class AffordabilityCalculator:
    """
    Computes cashflow impact and percentage allocations for a hypothetical buyout financing plan.
    Does not evaluate creditworthiness or grant approvals.
    """

    @staticmethod
    def calculate(
        new_monthly_income: float,
        existing_monthly_obligations: float,
        simulated_monthly_repayment: float,
    ) -> AffordabilityResult:
        if new_monthly_income <= 0:
            raise ValueError("Monthly income must be greater than zero.")
        if existing_monthly_obligations < 0:
            raise ValueError("Existing obligations cannot be negative.")
        if simulated_monthly_repayment <= 0:
            raise ValueError("Simulated monthly repayment must be greater than zero.")

        # Ratios
        repayment_ratio = round((simulated_monthly_repayment / new_monthly_income) * 100.0, 2)
        obligations_ratio = round((existing_monthly_obligations / new_monthly_income) * 100.0, 2)
        total_commitment_ratio = round(
            ((existing_monthly_obligations + simulated_monthly_repayment) / new_monthly_income) * 100.0, 2
        )

        remaining_after_obligations = round(new_monthly_income - existing_monthly_obligations, 2)
        remaining_after_repayment = round(
            new_monthly_income - existing_monthly_obligations - simulated_monthly_repayment, 2
        )

        # Neutral factual tone indicator based on common budgeting benchmarks (30% / 50%)
        # Strictly avoids "Approved", "Eligible", or credit labels.
        if total_commitment_ratio <= 35.0:
            status_tone = "healthy"
        elif total_commitment_ratio <= 50.0:
            status_tone = "moderate"
        else:
            status_tone = "high_commitment"

        summary = (
            f"Your simulated repayment of ₹{simulated_monthly_repayment:,.2f} represents "
            f"{repayment_ratio}% of the entered monthly income (₹{new_monthly_income:,.2f}). "
            f"Remaining monthly income after all entered commitments is ₹{remaining_after_repayment:,.2f} "
            f"({round((remaining_after_repayment / new_monthly_income) * 100, 1)}% of income)."
        )

        steps = [
            f"Entered new monthly income: ₹{new_monthly_income:,.2f}",
            f"Existing monthly debt obligations: ₹{existing_monthly_obligations:,.2f} ({obligations_ratio}% of income)",
            f"Simulated buyout monthly repayment: ₹{simulated_monthly_repayment:,.2f} ({repayment_ratio}% of income)",
            f"Net buffer after existing obligations: ₹{new_monthly_income:,.2f} - ₹{existing_monthly_obligations:,.2f} = ₹{remaining_after_obligations:,.2f}",
            f"Estimated remaining monthly income after simulated repayment: ₹{remaining_after_obligations:,.2f} - ₹{simulated_monthly_repayment:,.2f} = ₹{remaining_after_repayment:,.2f}",
        ]

        return AffordabilityResult(
            new_monthly_income=TaggedValue(
                value=new_monthly_income,
                origin=DataOrigin.USER_PROVIDED,
                source_description="User-entered monthly take-home pay at new employer"
            ),
            existing_monthly_obligations=TaggedValue(
                value=existing_monthly_obligations,
                origin=DataOrigin.USER_PROVIDED,
                source_description="User-entered recurring monthly debt commitments"
            ),
            simulated_monthly_repayment=TaggedValue(
                value=simulated_monthly_repayment,
                origin=DataOrigin.CALCULATED,
                formula="Calculated from NoticeBridge RepaymentEngine EMI"
            ),
            repayment_income_ratio_percent=TaggedValue(
                value=repayment_ratio,
                origin=DataOrigin.CALCULATED,
                formula=f"(₹{simulated_monthly_repayment:,.2f} / ₹{new_monthly_income:,.2f}) * 100"
            ),
            obligations_income_ratio_percent=TaggedValue(
                value=obligations_ratio,
                origin=DataOrigin.CALCULATED,
                formula=f"(₹{existing_monthly_obligations:,.2f} / ₹{new_monthly_income:,.2f}) * 100"
            ),
            remaining_income_after_obligations=TaggedValue(
                value=remaining_after_obligations,
                origin=DataOrigin.CALCULATED,
                formula=f"₹{new_monthly_income:,.2f} - ₹{existing_monthly_obligations:,.2f}"
            ),
            remaining_income_after_repayment=TaggedValue(
                value=remaining_after_repayment,
                origin=DataOrigin.CALCULATED,
                formula=f"₹{remaining_after_obligations:,.2f} - ₹{simulated_monthly_repayment:,.2f}"
            ),
            factual_summary=summary,
            status_tone=status_tone,
            breakdown_steps=steps,
        )

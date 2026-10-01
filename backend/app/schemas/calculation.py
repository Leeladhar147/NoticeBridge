from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from .origin import TaggedValue, DataOrigin, contract_derived, user_provided, calculated
from app.engines.buyout_engine import SalaryBasis, DivisorBasis
from app.engines.notice_engine import NoticeMilestone
from app.engines.repayment_engine import AmortizationEntry
from app.engines.scenario_engine import ScenarioResult

class NoticeCalculationRequest(BaseModel):
    contractual_notice_period: int = Field(..., gt=0, le=365, description="Contractual notice period in days")
    resignation_date: date = Field(..., description="Date resignation was or will be submitted")
    intended_joining_date: date = Field(..., description="Target joining date at new company")
    days_already_served: int = Field(default=0, ge=0, description="Notice days served so far")
    leave_adjustment_days: int = Field(default=0, ge=0, description="Leave days credited against notice")

    @field_validator("intended_joining_date")
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        resignation = info.data.get("resignation_date")
        if resignation and v < resignation:
            raise ValueError(f"intended_joining_date ({v}) cannot precede resignation_date ({resignation})")
        return v

class NoticeCalculationResponse(BaseModel):
    contractual_notice_days: TaggedValue[int]
    days_already_served: TaggedValue[int]
    leave_adjustment_days: TaggedValue[int]
    effective_served_days: TaggedValue[int]
    remaining_notice_days: TaggedValue[int]
    earliest_release_date: TaggedValue[date]
    intended_joining_date: TaggedValue[date]
    shortfall_days: TaggedValue[int]
    delay_days: TaggedValue[int]
    is_transition_feasible_without_buyout: TaggedValue[bool]
    status_summary: str
    timeline: List[NoticeMilestone]
    explanation: Dict[str, Any]

class BuyoutCalculationRequest(BaseModel):
    salary_amount: float = Field(..., gt=0, description="Monthly applicable salary")
    remaining_days: int = Field(..., ge=0, le=365, description="Notice shortfall or remaining days")
    salary_basis: SalaryBasis = Field(default=SalaryBasis.BASIC, description="Contract basis: basic, gross, fixed, custom")
    divisor_basis: DivisorBasis = Field(default=DivisorBasis.THIRTY_DAYS, description="30_days, 26_working_days, calendar_month, annual_365, custom")
    custom_divisor: Optional[float] = Field(default=None, gt=0, le=365)
    employer_contribution: float = Field(default=0.0, ge=0.0, description="New employer co-pay / buyout assistance")
    currency_symbol: str = Field(default="₹")

class BuyoutCalculationResponse(BaseModel):
    salary_basis: TaggedValue[str]
    salary_amount: TaggedValue[float]
    divisor_basis: TaggedValue[str]
    divisor_value: TaggedValue[float]
    remaining_days: TaggedValue[int]
    daily_rate: TaggedValue[float]
    gross_buyout_amount: TaggedValue[float]
    employer_contribution: TaggedValue[float]
    net_employee_payable: TaggedValue[float]
    formula_used: TaggedValue[str]
    detailed_steps: Dict[str, Any]

class RepaymentCalculationRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Buyout or bridge financing amount to simulate")
    duration_months: int = Field(default=6, ge=1, le=60, description="Repayment tenor in months")
    annual_interest_rate_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Annual percentage interest rate")
    service_fee_percent: float = Field(default=1.5, ge=0.0, le=20.0, description="Platform / processing service fee %")
    flat_service_fee: float = Field(default=0.0, ge=0.0)

class RepaymentCalculationResponse(BaseModel):
    principal_amount: TaggedValue[float]
    duration_months: TaggedValue[int]
    annual_interest_rate_percent: TaggedValue[float]
    total_service_fee: TaggedValue[float]
    monthly_repayment_amount: TaggedValue[float]
    total_interest_paid: TaggedValue[float]
    total_repayment_amount: TaggedValue[float]
    total_overall_cost: TaggedValue[float]
    effective_cost_ratio: TaggedValue[float]
    amortization_schedule: List[AmortizationEntry]
    formula_explanation: str
    breakdown: Dict[str, Any]

class ScenarioSimulationRequest(BaseModel):
    contractual_notice_period: int = Field(default=90, gt=0, le=365)
    resignation_date: date
    intended_joining_date: date
    days_already_served: int = Field(default=0, ge=0)
    leave_adjustment_days: int = Field(default=0, ge=0)
    monthly_salary: float = Field(..., gt=0)
    gross_monthly_salary: Optional[float] = Field(default=None, gt=0)
    salary_basis: SalaryBasis = Field(default=SalaryBasis.BASIC)
    divisor_basis: DivisorBasis = Field(default=DivisorBasis.THIRTY_DAYS)
    custom_divisor: Optional[float] = Field(default=None, gt=0)
    employer_offered_contribution: float = Field(default=0.0, ge=0.0)
    preferred_tenor_months: int = Field(default=6, ge=1, le=36)
    annual_interest_rate_percent: float = Field(default=10.0, ge=0.0, le=50.0)
    service_fee_percent: float = Field(default=1.0, ge=0.0, le=10.0)

class ScenarioSimulationResponse(BaseModel):
    baseline_notice: Any
    baseline_buyout: Any
    scenarios: List[ScenarioResult]
    summary_recommendation: str

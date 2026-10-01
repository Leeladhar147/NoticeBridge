from datetime import date, datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from .origin import TaggedValue, contract_derived, user_provided, calculated, DataOrigin

class CurrentEmploymentCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255, description="Current employer name")
    designation: str = Field(..., min_length=1, max_length=255, description="Current job title")
    joining_date: date = Field(..., description="Date joined current employer")
    resignation_date: Optional[date] = Field(default=None, description="Resignation date if already tendered")
    is_resigned: bool = Field(default=False)
    
    # Contractual details
    notice_period_days: int = Field(default=90, ge=1, le=365, description="Contractual notice period in days")
    buyout_clause_permitted: bool = Field(default=True, description="Whether contract permits notice buyout")
    buyout_salary_basis: str = Field(default="basic", description="Salary basis specified in contract: basic, gross, fixed, custom")
    monthly_divisor_basis: str = Field(default="30_days", description="Contract divisor: 30_days, 26_working_days, calendar_month, annual_365, custom")
    custom_divisor: Optional[float] = Field(default=None, ge=1.0, le=365.0)
    basic_salary_monthly: float = Field(..., gt=0, description="Monthly basic salary in INR")
    gross_salary_monthly: Optional[float] = Field(default=None, gt=0, description="Monthly gross salary in INR")
    clause_reference_notes: Optional[str] = Field(default=None, description="Excerpt or clause reference from employment contract")

    @field_validator("buyout_salary_basis")
    @classmethod
    def validate_basis(cls, v: str) -> str:
        valid = ["basic", "gross", "fixed", "custom"]
        if v.lower() not in valid:
            raise ValueError(f"buyout_salary_basis must be one of {valid}")
        return v.lower()

    @field_validator("monthly_divisor_basis")
    @classmethod
    def validate_divisor(cls, v: str) -> str:
        valid = ["30_days", "26_working_days", "calendar_month", "annual_365", "custom"]
        if v.lower() not in valid:
            raise ValueError(f"monthly_divisor_basis must be one of {valid}")
        return v.lower()

class CurrentEmploymentResponse(BaseModel):
    id: int
    company_name: TaggedValue[str]
    designation: TaggedValue[str]
    joining_date: TaggedValue[date]
    resignation_date: Optional[TaggedValue[date]]
    is_resigned: TaggedValue[bool]
    notice_period_days: TaggedValue[int]
    buyout_clause_permitted: TaggedValue[bool]
    buyout_salary_basis: TaggedValue[str]
    monthly_divisor_basis: TaggedValue[str]
    custom_divisor: Optional[TaggedValue[Optional[float]]]
    basic_salary_monthly: TaggedValue[float]
    gross_salary_monthly: Optional[TaggedValue[Optional[float]]]
    clause_reference_notes: Optional[TaggedValue[Optional[str]]]
    created_at: datetime

class NewOfferCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255, description="New offering company")
    designation: str = Field(..., min_length=1, max_length=255, description="New title")
    offered_ctc_annual: float = Field(..., gt=0, description="Offered annual CTC")
    target_joining_date: date = Field(..., description="Joining date required by new company")
    buyout_assistance_amount: float = Field(default=0.0, ge=0.0, description="Notice buyout coverage offered by new employer")
    signing_bonus: float = Field(default=0.0, ge=0.0, description="Joining or signing bonus")
    retention_clawback_months: int = Field(default=0, ge=0, le=60)

class NewOfferResponse(BaseModel):
    id: int
    company_name: TaggedValue[str]
    designation: TaggedValue[str]
    offered_ctc_annual: TaggedValue[float]
    target_joining_date: TaggedValue[date]
    buyout_assistance_amount: TaggedValue[float]
    signing_bonus: TaggedValue[float]
    retention_clawback_months: TaggedValue[int]
    created_at: datetime

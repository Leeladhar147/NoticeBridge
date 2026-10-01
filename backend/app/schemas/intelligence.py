from datetime import date
from enum import Enum
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field
from .origin import DataOrigin, TaggedValue

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"

T = TypeVar("T")

class ExtractedSourceField(BaseModel, Generic[T]):
    """
    Source-grounded extracted field holding the value, evidence citation,
    page number, section reference, confidence, and confirmation state.
    """
    value: T
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH
    source_document: str = "Unknown"
    page_number: Optional[int] = None
    section_reference: Optional[str] = None
    evidence_quote: Optional[str] = None
    is_confirmed_by_user: bool = False
    status_message: Optional[str] = None
    provenance: DataOrigin = DataOrigin.CONTRACT_DERIVED

class RetrievedClause(BaseModel):
    query_intent: str
    relevance_score: float
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    text_content: str
    is_applicable: bool = True

class ContractIntelligenceResponse(BaseModel):
    document_id: int
    document_name: str
    company_name: ExtractedSourceField[Optional[str]]
    notice_period_days: ExtractedSourceField[Optional[int]]
    notice_unit: ExtractedSourceField[str]
    is_notice_conditional: ExtractedSourceField[bool]
    notice_conditions: ExtractedSourceField[Optional[str]]
    buyout_permitted: ExtractedSourceField[Optional[bool]]
    early_release_mentioned: ExtractedSourceField[Optional[bool]]
    buyout_salary_basis: ExtractedSourceField[Optional[str]]
    monthly_divisor: ExtractedSourceField[Optional[float]]
    basic_salary_monthly: ExtractedSourceField[Optional[float]]
    gross_salary_monthly: ExtractedSourceField[Optional[float]]
    retrieved_clauses: List[RetrievedClause]
    overall_confidence: str
    requires_user_confirmation: bool
    uncertain_fields: List[str]

class OfferIntelligenceResponse(BaseModel):
    document_id: int
    document_name: str
    offering_company: ExtractedSourceField[Optional[str]]
    role_title: ExtractedSourceField[Optional[str]]
    target_joining_date: ExtractedSourceField[Optional[date]]
    offered_ctc_annual: ExtractedSourceField[Optional[float]]
    buyout_assistance_amount: ExtractedSourceField[Optional[float]]
    signing_bonus: ExtractedSourceField[Optional[float]]
    retention_clawback_months: ExtractedSourceField[Optional[int]]
    retrieved_clauses: List[RetrievedClause]
    overall_confidence: str
    requires_user_confirmation: bool
    uncertain_fields: List[str]

class ContractConfirmationRequest(BaseModel):
    document_id: int
    company_name: str
    notice_period_days: int
    buyout_clause_permitted: bool
    buyout_salary_basis: str  # basic, gross, fixed, custom
    monthly_divisor_basis: str  # 30_days, 26_working_days, calendar_month, annual_365, custom
    custom_divisor: Optional[float] = None
    basic_salary_monthly: float
    gross_salary_monthly: Optional[float] = None
    clause_reference_notes: Optional[str] = None

class AffordabilitySimulationRequest(BaseModel):
    new_monthly_income: float = Field(..., gt=0, description="Monthly in-hand / take-home pay at new company")
    existing_monthly_obligations: float = Field(default=0.0, ge=0, description="Existing recurring monthly debt/EMI obligations")
    simulated_monthly_repayment: float = Field(..., gt=0, description="Notice buyout simulated monthly EMI")

class AffordabilitySimulationResponse(BaseModel):
    new_monthly_income: TaggedValue[float]
    existing_monthly_obligations: TaggedValue[float]
    simulated_monthly_repayment: TaggedValue[float]
    repayment_income_ratio_percent: TaggedValue[float]
    obligations_income_ratio_percent: TaggedValue[float]
    remaining_income_after_obligations: TaggedValue[float]
    remaining_income_after_repayment: TaggedValue[float]
    factual_summary: str
    status_tone: str  # "healthy", "moderate", "high_commitment"

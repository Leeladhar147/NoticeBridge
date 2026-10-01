"""
Validation Service for NoticeBridge.
Strict architectural gatekeeper sitting between AI/RAG extraction
and the deterministic Python calculation engines.
Rejects contradictory, negative, impossible, or ungrounded values.
"""

from datetime import date
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

from app.schemas.intelligence import (
    ContractIntelligenceResponse,
    OfferIntelligenceResponse,
    ContractConfirmationRequest,
    ConfidenceLevel,
)
from app.engines.buyout_engine import SalaryBasis, DivisorBasis


class ValidationResult(BaseModel):
    is_valid: bool
    requires_user_action: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    sanitized_contract_data: Optional[Dict[str, Any]] = None


class ExtractionValidationService:
    """
    Validates extracted values before they can be saved to the database or ingested
    by the deterministic engine. Enforces anti-hallucination standards.
    """

    @staticmethod
    def validate_extracted_contract(extraction: ContractIntelligenceResponse) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []
        requires_user_action = False

        # 1. Notice period validation
        notice_val = extraction.notice_period_days.value
        if notice_val is None:
            warnings.append("Notice period was not explicitly detected in contract. User confirmation required.")
            requires_user_action = True
        elif not (0 < notice_val <= 365):
            errors.append(f"Detected notice period ({notice_val} days) is outside realistic bounds (1 to 365 days).")
            requires_user_action = True

        # 2. Buyout availability validation
        buyout_val = extraction.buyout_permitted.value
        if buyout_val is None:
            warnings.append("Notice buyout / early release clause was not explicitly confirmed. Marked as Unknown.")
            requires_user_action = True
        elif extraction.buyout_permitted.confidence in [ConfidenceLevel.LOW, ConfidenceLevel.UNKNOWN]:
            warnings.append("Buyout clause confidence is low or uncertain. Manual verification required.")
            requires_user_action = True

        # 3. Salary Basis validation
        salary_basis_val = extraction.buyout_salary_basis.value
        valid_bases = [b.value for b in SalaryBasis]
        if salary_basis_val and salary_basis_val.lower() not in valid_bases and salary_basis_val.lower() != "unknown":
            errors.append(f"Unrecognized salary basis '{salary_basis_val}'. Allowed: {valid_bases}.")
            requires_user_action = True

        # 4. Salary amounts
        basic_salary = extraction.basic_salary_monthly.value
        gross_salary = extraction.gross_salary_monthly.value

        if basic_salary is not None and basic_salary <= 0:
            errors.append(f"Basic monthly salary cannot be zero or negative (got {basic_salary}).")
        if gross_salary is not None and gross_salary <= 0:
            errors.append(f"Gross monthly salary cannot be zero or negative (got {gross_salary}).")
        if basic_salary is not None and gross_salary is not None:
            if basic_salary > gross_salary:
                errors.append(
                    f"Contradictory salary data: basic salary (₹{basic_salary:,.2f}) "
                    f"cannot exceed gross salary (₹{gross_salary:,.2f})."
                )

        if extraction.uncertain_fields:
            requires_user_action = True
            warnings.append(f"Uncertain fields flagged for review: {', '.join(extraction.uncertain_fields)}")

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            requires_user_action=requires_user_action or not is_valid,
            errors=errors,
            warnings=warnings,
            sanitized_contract_data={
                "notice_period_days": notice_val,
                "buyout_permitted": buyout_val,
                "salary_basis": salary_basis_val,
                "basic_salary": basic_salary,
                "gross_salary": gross_salary,
            }
        )

    @staticmethod
    def validate_user_confirmation(confirmation: ContractConfirmationRequest) -> Tuple[bool, List[str]]:
        """
        Validates the user's manual review/confirmation payload before updating contract entities.
        """
        errors: List[str] = []

        if not (1 <= confirmation.notice_period_days <= 365):
            errors.append("Notice period must be between 1 and 365 days.")

        if confirmation.basic_salary_monthly <= 0:
            errors.append("Basic monthly salary must be strictly greater than zero.")

        if confirmation.gross_salary_monthly is not None:
            if confirmation.gross_salary_monthly <= 0:
                errors.append("Gross monthly salary cannot be negative or zero.")
            if confirmation.gross_salary_monthly < confirmation.basic_salary_monthly:
                errors.append("Gross monthly salary cannot be less than basic monthly salary.")

        # Divisor validation
        if confirmation.monthly_divisor_basis == "custom":
            if not confirmation.custom_divisor or confirmation.custom_divisor <= 0:
                errors.append("Custom monthly divisor must be specified and positive.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_extracted_offer(extraction: OfferIntelligenceResponse) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []
        requires_user_action = False

        joining_date_val = extraction.target_joining_date.value
        if joining_date_val is None:
            warnings.append("Target joining date not detected in offer document. User must specify manually.")
            requires_user_action = True
        elif joining_date_val < date.today():
            warnings.append(f"Target joining date ({joining_date_val}) is in the past. Verify with user.")
            requires_user_action = True

        offered_ctc = extraction.offered_ctc_annual.value
        if offered_ctc is not None and offered_ctc <= 0:
            errors.append("Annual CTC cannot be zero or negative.")

        buyout_assist = extraction.buyout_assistance_amount.value
        if buyout_assist is not None and buyout_assist < 0:
            errors.append("Buyout assistance cannot be negative.")

        if extraction.uncertain_fields:
            requires_user_action = True

        return ValidationResult(
            is_valid=len(errors) == 0,
            requires_user_action=requires_user_action or len(errors) > 0,
            errors=errors,
            warnings=warnings,
            sanitized_contract_data={
                "target_joining_date": joining_date_val,
                "offered_ctc_annual": offered_ctc,
                "buyout_assistance_amount": buyout_assist,
            }
        )

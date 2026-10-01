from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class SalaryBasis(str, Enum):
    BASIC = "basic"
    GROSS = "gross"
    FIXED = "fixed"
    CUSTOM = "custom"

class DivisorBasis(str, Enum):
    THIRTY_DAYS = "30_days"
    TWENTY_SIX_DAYS = "26_working_days"
    CALENDAR_MONTH = "calendar_month"
    ANNUAL_365 = "annual_365"
    CUSTOM_DIVISOR = "custom"

class BuyoutResult(BaseModel):
    salary_basis: SalaryBasis
    salary_amount: float
    divisor_basis: DivisorBasis
    divisor_value: float
    remaining_days: int
    daily_rate: float
    gross_buyout_amount: float
    employer_contribution: float
    net_employee_payable: float
    formula_used: str
    detailed_steps: Dict[str, Any]

class BuyoutCalculator:
    """
    Deterministic Buyout Calculator.
    Calculates notice buyout costs across configurable salary bases,
    day divisors, and employer contribution structures.
    """

    @staticmethod
    def resolve_divisor(
        divisor_basis: DivisorBasis,
        custom_divisor: Optional[float] = None,
        days_in_month: int = 30
    ) -> float:
        if divisor_basis == DivisorBasis.THIRTY_DAYS:
            return 30.0
        elif divisor_basis == DivisorBasis.TWENTY_SIX_DAYS:
            return 26.0
        elif divisor_basis == DivisorBasis.CALENDAR_MONTH:
            return float(days_in_month) if days_in_month in [28, 29, 30, 31] else 30.0
        elif divisor_basis == DivisorBasis.ANNUAL_365:
            # 365 / 12 months = 30.416666...
            return 365.0 / 12.0
        elif divisor_basis == DivisorBasis.CUSTOM_DIVISOR:
            if not custom_divisor or custom_divisor <= 0:
                raise ValueError(f"Custom divisor must be positive. Received: {custom_divisor}")
            return float(custom_divisor)
        return 30.0

    @classmethod
    def calculate(
        cls,
        salary_amount: float,
        remaining_days: int,
        salary_basis: SalaryBasis = SalaryBasis.BASIC,
        divisor_basis: DivisorBasis = DivisorBasis.THIRTY_DAYS,
        custom_divisor: Optional[float] = None,
        days_in_month: int = 30,
        employer_contribution: float = 0.0,
        currency_symbol: str = "₹"
    ) -> BuyoutResult:
        # Validations
        if salary_amount <= 0:
            raise ValueError(f"Salary amount must be strictly positive (>0). Received: {salary_amount}")
        if remaining_days < 0:
            raise ValueError(f"Remaining days cannot be negative. Received: {remaining_days}")
        if employer_contribution < 0:
            raise ValueError(f"Employer contribution cannot be negative. Received: {employer_contribution}")

        divisor_val = cls.resolve_divisor(divisor_basis, custom_divisor, days_in_month)

        # Deterministic Daily Rate
        # Daily rate = Monthly applicable salary / divisor
        daily_rate_raw = salary_amount / divisor_val
        daily_rate = round(daily_rate_raw, 4)

        # Gross buyout = Daily rate * remaining unserved notice days
        gross_buyout_raw = daily_rate * remaining_days
        gross_buyout_amount = round(gross_buyout_raw, 2)

        # Employer co-pay or signing buyout assistance
        applied_contribution = min(gross_buyout_amount, employer_contribution)
        net_payable_raw = max(0.0, gross_buyout_amount - applied_contribution)
        net_employee_payable = round(net_payable_raw, 2)

        # Clean explainable formula display string
        # e.g., ₹60,000 / 30 × 60 = ₹120,000
        divisor_str = f"{int(divisor_val)}" if divisor_val.is_integer() else f"{divisor_val:.2f}"
        formula_used = (
            f"({currency_symbol}{salary_amount:,.2f} / {divisor_str}) × {remaining_days} days = "
            f"{currency_symbol}{gross_buyout_amount:,.2f}"
        )

        detailed_steps = {
            "step_1_applicable_salary": {
                "salary_basis": salary_basis.value,
                "amount": salary_amount,
                "description": f"Applicable {salary_basis.value.capitalize()} monthly salary used as contractual base."
            },
            "step_2_daily_rate": {
                "divisor_basis": divisor_basis.value,
                "divisor_value": divisor_val,
                "daily_rate": daily_rate,
                "calculation": f"{salary_amount} / {divisor_val} = {daily_rate:.4f} per day"
            },
            "step_3_gross_buyout": {
                "remaining_days": remaining_days,
                "gross_amount": gross_buyout_amount,
                "calculation": f"{daily_rate:.4f} × {remaining_days} = {gross_buyout_amount:.2f}"
            },
            "step_4_net_payable": {
                "employer_contribution_requested": employer_contribution,
                "employer_contribution_applied": applied_contribution,
                "net_employee_payable": net_employee_payable,
                "calculation": f"max(0.0, {gross_buyout_amount} - {applied_contribution}) = {net_employee_payable:.2f}"
            }
        }

        return BuyoutResult(
            salary_basis=salary_basis,
            salary_amount=salary_amount,
            divisor_basis=divisor_basis,
            divisor_value=divisor_val,
            remaining_days=remaining_days,
            daily_rate=daily_rate,
            gross_buyout_amount=gross_buyout_amount,
            employer_contribution=employer_contribution,
            net_employee_payable=net_employee_payable,
            formula_used=formula_used,
            detailed_steps=detailed_steps
        )

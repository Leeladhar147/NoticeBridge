import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AmortizationEntry(BaseModel):
    month: int
    opening_balance: float
    installment_amount: float
    principal_component: float
    interest_component: float
    closing_balance: float

class RepaymentSimulationResult(BaseModel):
    principal_amount: float
    duration_months: int
    annual_interest_rate_percent: float
    service_fee_percent: float
    flat_service_fee: float
    total_service_fee: float
    monthly_repayment_amount: float
    total_interest_paid: float
    total_repayment_amount: float
    total_overall_cost: float
    effective_cost_ratio: float
    amortization_schedule: List[AmortizationEntry]
    formula_explanation: str
    breakdown: Dict[str, Any]

class RepaymentCalculator:
    """
    Deterministic Repayment and Financing Simulation Engine.
    Computes exact fixed EMI, full amortization schedule, fee structures,
    and effective total repayment without reliance on approximations or black boxes.
    """

    @classmethod
    def calculate(
        cls,
        principal: float,
        duration_months: int,
        annual_interest_rate_percent: float = 0.0,
        service_fee_percent: float = 1.5,
        flat_service_fee: float = 0.0
    ) -> RepaymentSimulationResult:
        # Validations
        if principal <= 0:
            raise ValueError(f"Principal amount must be strictly positive. Received: {principal}")
        if duration_months <= 0:
            raise ValueError(f"Duration in months must be at least 1 month. Received: {duration_months}")
        if annual_interest_rate_percent < 0:
            raise ValueError(
                f"Annual interest rate cannot be negative. Received: {annual_interest_rate_percent}"
            )
        if service_fee_percent < 0:
            raise ValueError(f"Service fee percentage cannot be negative. Received: {service_fee_percent}")
        if flat_service_fee < 0:
            raise ValueError(f"Flat service fee cannot be negative. Received: {flat_service_fee}")

        # Compute service fee
        percentage_fee = round(principal * (service_fee_percent / 100.0), 2)
        total_service_fee = round(flat_service_fee + percentage_fee, 2)

        # Compute monthly repayment (EMI)
        n = duration_months
        if annual_interest_rate_percent == 0.0:
            monthly_repayment = round(principal / n, 2)
            formula_explanation = f"Zero-interest EMI: Principal ({principal:,.2f}) / {n} months = {monthly_repayment:,.2f}/mo"
        else:
            monthly_rate = (annual_interest_rate_percent / 100.0) / 12.0
            factor = math.pow(1.0 + monthly_rate, n)
            # EMI = P * r * (1+r)^n / ((1+r)^n - 1)
            raw_emi = principal * (monthly_rate * factor) / (factor - 1.0)
            monthly_repayment = round(raw_emi, 2)
            formula_explanation = (
                f"Amortized EMI: {principal:,.2f} × [{monthly_rate:.5f} × (1+{monthly_rate:.5f})^{n}] / "
                f"[(1+{monthly_rate:.5f})^{n} - 1] = {monthly_repayment:,.2f}/mo @ {annual_interest_rate_percent}% p.a."
            )

        # Build full amortization schedule
        schedule: List[AmortizationEntry] = []
        balance = principal
        total_interest = 0.0
        monthly_rate = (annual_interest_rate_percent / 100.0) / 12.0 if annual_interest_rate_percent > 0 else 0.0

        for m in range(1, n + 1):
            opening = round(balance, 2)
            if monthly_rate > 0:
                interest_comp = round(opening * monthly_rate, 2)
            else:
                interest_comp = 0.0

            # On final month, adjust for rounding so closing balance reaches 0.00 exactly
            if m == n:
                principal_comp = round(opening, 2)
                installment = round(principal_comp + interest_comp, 2)
                closing = 0.0
            else:
                principal_comp = round(monthly_repayment - interest_comp, 2)
                # Safeguard if principal_comp > opening due to rounding
                if principal_comp > opening:
                    principal_comp = opening
                installment = round(principal_comp + interest_comp, 2)
                closing = round(opening - principal_comp, 2)

            total_interest += interest_comp
            balance = closing

            schedule.append(
                AmortizationEntry(
                    month=m,
                    opening_balance=opening,
                    installment_amount=installment,
                    principal_component=principal_comp,
                    interest_component=interest_comp,
                    closing_balance=closing
                )
            )

        total_interest_paid = round(total_interest, 2)
        total_repayment_amount = round(principal + total_interest_paid, 2)
        total_overall_cost = round(total_repayment_amount + total_service_fee, 2)
        effective_cost_ratio = round((total_overall_cost / principal), 4)

        breakdown = {
            "principal": principal,
            "tenor_months": duration_months,
            "monthly_emi": monthly_repayment,
            "total_interest": total_interest_paid,
            "service_fee": total_service_fee,
            "total_repayment": total_repayment_amount,
            "total_overall_cost": total_overall_cost,
            "net_finance_burden": round(total_overall_cost - principal, 2)
        }

        return RepaymentSimulationResult(
            principal_amount=principal,
            duration_months=duration_months,
            annual_interest_rate_percent=annual_interest_rate_percent,
            service_fee_percent=service_fee_percent,
            flat_service_fee=flat_service_fee,
            total_service_fee=total_service_fee,
            monthly_repayment_amount=monthly_repayment,
            total_interest_paid=total_interest_paid,
            total_repayment_amount=total_repayment_amount,
            total_overall_cost=total_overall_cost,
            effective_cost_ratio=effective_cost_ratio,
            amortization_schedule=schedule,
            formula_explanation=formula_explanation,
            breakdown=breakdown
        )

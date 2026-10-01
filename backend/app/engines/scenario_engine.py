from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from .notice_engine import NoticePeriodCalculator, NoticeResult
from .buyout_engine import BuyoutCalculator, BuyoutResult, SalaryBasis, DivisorBasis
from .repayment_engine import RepaymentCalculator, RepaymentSimulationResult

class ScenarioResult(BaseModel):
    id: str
    title: str
    scenario_type: str  # "full_notice", "full_buyout", "employer_co_pay", "repayment_variant", "basis_variant", "extended_notice"
    tagline: str
    pros: List[str]
    cons: List[str]
    joining_date: date
    delay_in_joining_days: int
    gross_buyout_cost: float
    employer_contribution: float
    net_employee_liability: float
    monthly_repayment_estimate: float
    repayment_tenor_months: int
    total_repayment_cost: float
    is_financially_lightest: bool = False
    is_fastest_transition: bool = False
    is_recommended: bool = False
    details: Dict[str, Any]

class ScenarioComparisonMatrix(BaseModel):
    baseline_notice: NoticeResult
    baseline_buyout: BuyoutResult
    scenarios: List[ScenarioResult]
    summary_recommendation: str

class ScenarioEngine:
    """
    Deterministic Scenario Simulator Engine.
    Simulates, ranks, and compares multiple transition strategies without guesswork.
    """

    @classmethod
    def simulate(
        cls,
        contractual_notice_period: int,
        resignation_date: date,
        intended_joining_date: date,
        days_already_served: int,
        leave_adjustment_days: int,
        monthly_salary: float,
        gross_monthly_salary: Optional[float] = None,
        salary_basis: SalaryBasis = SalaryBasis.BASIC,
        divisor_basis: DivisorBasis = DivisorBasis.THIRTY_DAYS,
        custom_divisor: Optional[float] = None,
        employer_offered_contribution: float = 0.0,
        preferred_tenor_months: int = 6,
        annual_interest_rate_percent: float = 10.0,
        service_fee_percent: float = 1.0,
    ) -> ScenarioComparisonMatrix:
        
        # 1. Baseline Notice
        notice_res = NoticePeriodCalculator.calculate(
            contractual_notice_period=contractual_notice_period,
            resignation_date=resignation_date,
            intended_joining_date=intended_joining_date,
            days_already_served=days_already_served,
            leave_adjustment_days=leave_adjustment_days
        )

        remaining_days = notice_res.remaining_notice_days
        shortfall_days = notice_res.shortfall_days

        # 2. Baseline Buyout for Shortfall Days
        # Notice buyout is needed for the shortfall (unserved notice days before joining)
        buyout_target_days = shortfall_days if shortfall_days > 0 else 0

        baseline_buyout = BuyoutCalculator.calculate(
            salary_amount=monthly_salary,
            remaining_days=buyout_target_days,
            salary_basis=salary_basis,
            divisor_basis=divisor_basis,
            custom_divisor=custom_divisor,
            employer_contribution=employer_offered_contribution
        )

        scenarios: List[ScenarioResult] = []

        # ==========================================
        # Scenario 1: Serve Full Notice (No Buyout)
        # ==========================================
        scenarios.append(
            ScenarioResult(
                id="scenario-1-full-notice",
                title="Serve Full Notice Period",
                scenario_type="full_notice",
                tagline="Zero financial liability, but delays start date at new employer.",
                pros=[
                    "Zero out-of-pocket buyout expense",
                    "No loans or repayment obligations",
                    "Clean exit in full accordance with contractual tenure"
                ],
                cons=[
                    f"Delays joining by {notice_res.delay_days} days until {notice_res.earliest_release_date.isoformat()}",
                    "Risk of offer withdrawal if new employer has strict onboarding deadlines"
                ],
                joining_date=notice_res.earliest_release_date,
                delay_in_joining_days=notice_res.delay_days,
                gross_buyout_cost=0.0,
                employer_contribution=0.0,
                net_employee_liability=0.0,
                monthly_repayment_estimate=0.0,
                repayment_tenor_months=0,
                total_repayment_cost=0.0,
                is_financially_lightest=True,
                is_fastest_transition=False,
                is_recommended=(notice_res.shortfall_days == 0),
                details={
                    "strategy": "Serve all remaining contractual notice days without buyout.",
                    "earliest_release_date": notice_res.earliest_release_date.isoformat(),
                    "total_served_days": contractual_notice_period
                }
            )
        )

        # ==========================================
        # Scenario 2: Serve Partial Notice + Full Buyout
        # ==========================================
        if buyout_target_days > 0:
            full_buyout_res = BuyoutCalculator.calculate(
                salary_amount=monthly_salary,
                remaining_days=buyout_target_days,
                salary_basis=salary_basis,
                divisor_basis=divisor_basis,
                custom_divisor=custom_divisor,
                employer_contribution=0.0
            )

            # Repayment calculation for full buyout amount
            repay_res = RepaymentCalculator.calculate(
                principal=full_buyout_res.net_employee_payable,
                duration_months=preferred_tenor_months,
                annual_interest_rate_percent=annual_interest_rate_percent,
                service_fee_percent=service_fee_percent
            )

            scenarios.append(
                ScenarioResult(
                    id="scenario-2-full-buyout",
                    title="Employee-Funded Early Buyout",
                    scenario_type="full_buyout",
                    tagline="Join on time with structured monthly repayment bridging the gap.",
                    pros=[
                        f"Guarantees prompt joining on {intended_joining_date.isoformat()} without delay",
                        "Secures new offer immediately",
                        f"Predictable monthly EMI of ₹{repay_res.monthly_repayment_amount:,.2f} over {preferred_tenor_months} months"
                    ],
                    cons=[
                        f"Full out-of-pocket liability of ₹{full_buyout_res.net_employee_payable:,.2f}",
                        f"Incurs ₹{repay_res.total_interest_paid + repay_res.total_service_fee:,.2f} financing and fee costs"
                    ],
                    joining_date=intended_joining_date,
                    delay_in_joining_days=0,
                    gross_buyout_cost=full_buyout_res.gross_buyout_amount,
                    employer_contribution=0.0,
                    net_employee_liability=full_buyout_res.net_employee_payable,
                    monthly_repayment_estimate=repay_res.monthly_repayment_amount,
                    repayment_tenor_months=preferred_tenor_months,
                    total_repayment_cost=repay_res.total_overall_cost,
                    is_financially_lightest=False,
                    is_fastest_transition=True,
                    is_recommended=(notice_res.shortfall_days > 0 and notice_res.shortfall_days <= 15 and employer_offered_contribution <= 0),
                    details={
                        "strategy": f"Buy out {buyout_target_days} shortfall days using structured monthly financing.",
                        "formula": full_buyout_res.formula_used,
                        "emi_breakdown": repay_res.breakdown
                    }
                )
            )

        # ==========================================
        # Scenario 3: Employer Contribution / Co-Pay
        # ==========================================
        if buyout_target_days > 0:
            effective_employer_contrib = employer_offered_contribution if employer_offered_contribution > 0 else round(baseline_buyout.gross_buyout_amount * 0.5, 2)
            co_buyout = BuyoutCalculator.calculate(
                salary_amount=monthly_salary,
                remaining_days=buyout_target_days,
                salary_basis=salary_basis,
                divisor_basis=divisor_basis,
                custom_divisor=custom_divisor,
                employer_contribution=effective_employer_contrib
            )

            co_principal = max(1.0, co_buyout.net_employee_payable)
            co_repay = RepaymentCalculator.calculate(
                principal=co_principal,
                duration_months=preferred_tenor_months,
                annual_interest_rate_percent=annual_interest_rate_percent,
                service_fee_percent=service_fee_percent
            ) if co_buyout.net_employee_payable > 0 else None

            scenarios.append(
                ScenarioResult(
                    id="scenario-3-employer-co-pay",
                    title="Employer Co-Sponsored Transition",
                    scenario_type="employer_co_pay",
                    tagline="New employer covers portion of buyout (joining bonus/buyout assistance).",
                    pros=[
                        f"Reduces personal liability by ₹{effective_employer_contrib:,.2f}",
                        "Timely joining on target date",
                        f"Lower monthly EMI burden (₹{co_repay.monthly_repayment_amount:,.2f}/mo)" if co_repay else "100% employer covered"
                    ],
                    cons=[
                        "Requires negotiation with new employer",
                        "May include retention clawback clause at new company (e.g. 1-year lock-in)"
                    ],
                    joining_date=intended_joining_date,
                    delay_in_joining_days=0,
                    gross_buyout_cost=co_buyout.gross_buyout_amount,
                    employer_contribution=effective_employer_contrib,
                    net_employee_liability=co_buyout.net_employee_payable,
                    monthly_repayment_estimate=co_repay.monthly_repayment_amount if co_repay else 0.0,
                    repayment_tenor_months=preferred_tenor_months if co_repay else 0,
                    total_repayment_cost=co_repay.total_overall_cost if co_repay else 0.0,
                    is_financially_lightest=False,
                    is_fastest_transition=True,
                    is_recommended=(employer_offered_contribution > 0),
                    details={
                        "employer_contribution_mode": "Contract buyout bonus / early joining assistance",
                        "contribution_amount": effective_employer_contrib,
                        "employee_net_share": co_buyout.net_employee_payable
                    }
                )
            )

        # ==========================================
        # Scenario 4: Different Repayment Tenors (12 Months Extended)
        # ==========================================
        if buyout_target_days > 0 and baseline_buyout.net_employee_payable > 0:
            tenor_12_repay = RepaymentCalculator.calculate(
                principal=baseline_buyout.net_employee_payable,
                duration_months=12,
                annual_interest_rate_percent=annual_interest_rate_percent,
                service_fee_percent=service_fee_percent
            )

            scenarios.append(
                ScenarioResult(
                    id="scenario-4-repayment-12m",
                    title="12-Month Extended Liquidity",
                    scenario_type="repayment_variant",
                    tagline="Lowest monthly cash burden for maximum breathing room.",
                    pros=[
                        f"Lowest monthly EMI: ₹{tenor_12_repay.monthly_repayment_amount:,.2f}/month",
                        "Minimizes initial monthly cashflow impact during job change"
                    ],
                    cons=[
                        f"Higher total interest over 12 months (₹{tenor_12_repay.total_interest_paid:,.2f})"
                    ],
                    joining_date=intended_joining_date,
                    delay_in_joining_days=0,
                    gross_buyout_cost=baseline_buyout.gross_buyout_amount,
                    employer_contribution=baseline_buyout.employer_contribution,
                    net_employee_liability=baseline_buyout.net_employee_payable,
                    monthly_repayment_estimate=tenor_12_repay.monthly_repayment_amount,
                    repayment_tenor_months=12,
                    total_repayment_cost=tenor_12_repay.total_overall_cost,
                    is_financially_lightest=False,
                    is_fastest_transition=True,
                    is_recommended=False,
                    details={
                        "tenor": 12,
                        "monthly_emi": tenor_12_repay.monthly_repayment_amount,
                        "total_interest": tenor_12_repay.total_interest_paid
                    }
                )
            )

        # ==========================================
        # Scenario 5: Different Contractual Salary Basis (Gross vs Basic)
        # ==========================================
        if buyout_target_days > 0:
            comparison_salary = gross_monthly_salary if gross_monthly_salary else round(monthly_salary * 1.6, 2)
            alt_basis = SalaryBasis.GROSS if salary_basis == SalaryBasis.BASIC else SalaryBasis.BASIC
            alt_buyout = BuyoutCalculator.calculate(
                salary_amount=comparison_salary if alt_basis == SalaryBasis.GROSS else monthly_salary,
                remaining_days=buyout_target_days,
                salary_basis=alt_basis,
                divisor_basis=divisor_basis,
                custom_divisor=custom_divisor,
                employer_contribution=employer_offered_contribution
            )

            scenarios.append(
                ScenarioResult(
                    id="scenario-5-salary-basis-variant",
                    title=f"Contract Clause: {alt_basis.value.capitalize()} Salary Basis",
                    scenario_type="basis_variant",
                    tagline=f"Financial exposure if contract stipulates {alt_basis.value} pay rather than {salary_basis.value} pay.",
                    pros=[
                        f"Provides exact contractual clarity if company audits policy basis"
                    ],
                    cons=[
                        f"Changes buyout liability to ₹{alt_buyout.net_employee_payable:,.2f}"
                    ],
                    joining_date=intended_joining_date,
                    delay_in_joining_days=0,
                    gross_buyout_cost=alt_buyout.gross_buyout_amount,
                    employer_contribution=alt_buyout.employer_contribution,
                    net_employee_liability=alt_buyout.net_employee_payable,
                    monthly_repayment_estimate=round(alt_buyout.net_employee_payable / preferred_tenor_months, 2),
                    repayment_tenor_months=preferred_tenor_months,
                    total_repayment_cost=alt_buyout.net_employee_payable,
                    is_financially_lightest=False,
                    is_fastest_transition=True,
                    is_recommended=False,
                    details={
                        "contract_basis": alt_basis.value,
                        "formula": alt_buyout.formula_used,
                        "salary_evaluated": comparison_salary
                    }
                )
            )

        # ==========================================
        # Scenario 6: Negotiate +15 Days Extended Service
        # ==========================================
        if buyout_target_days > 15:
            negotiated_served = days_already_served + 15
            reduced_shortfall = max(0, shortfall_days - 15)
            reduced_buyout = BuyoutCalculator.calculate(
                salary_amount=monthly_salary,
                remaining_days=reduced_shortfall,
                salary_basis=salary_basis,
                divisor_basis=divisor_basis,
                custom_divisor=custom_divisor,
                employer_contribution=employer_offered_contribution
            )

            new_joining = intended_joining_date + timedelta(days=15)
            reduced_repay = RepaymentCalculator.calculate(
                principal=max(1.0, reduced_buyout.net_employee_payable),
                duration_months=preferred_tenor_months,
                annual_interest_rate_percent=annual_interest_rate_percent,
                service_fee_percent=service_fee_percent
            ) if reduced_buyout.net_employee_payable > 0 else None

            scenarios.append(
                ScenarioResult(
                    id="scenario-6-negotiated-service",
                    title="Serve Extra 15 Days + Reduced Buyout",
                    scenario_type="extended_notice",
                    tagline="Serve 15 additional days to slash buyout liability by half.",
                    pros=[
                        f"Saves ₹{baseline_buyout.gross_buyout_amount - reduced_buyout.gross_buyout_amount:,.2f} in notice buyout fees",
                        "Smoother knowledge handover builds goodwill with current employer",
                        f"Lower monthly EMI: ₹{reduced_repay.monthly_repayment_amount:,.2f}/mo" if reduced_repay else "₹0"
                    ],
                    cons=[
                        f"Requires new employer to accept a 15-day delayed start date ({new_joining.isoformat()})"
                    ],
                    joining_date=new_joining,
                    delay_in_joining_days=15,
                    gross_buyout_cost=reduced_buyout.gross_buyout_amount,
                    employer_contribution=reduced_buyout.employer_contribution,
                    net_employee_liability=reduced_buyout.net_employee_payable,
                    monthly_repayment_estimate=reduced_repay.monthly_repayment_amount if reduced_repay else 0.0,
                    repayment_tenor_months=preferred_tenor_months if reduced_repay else 0,
                    total_repayment_cost=reduced_repay.total_overall_cost if reduced_repay else 0.0,
                    is_financially_lightest=False,
                    is_fastest_transition=False,
                    is_recommended=(notice_res.shortfall_days > 15 and employer_offered_contribution <= 0),
                    details={
                        "strategy": "Serve additional 15 days, reducing buyout shortfall",
                        "days_saved": 15,
                        "adjusted_joining_date": new_joining.isoformat()
                    }
                )
            )

        # Summary recommendation
        if notice_res.shortfall_days == 0:
            rec = "Transition is fully feasible without notice buyout. Complete your standard notice."
        elif employer_offered_contribution > 0:
            rec = "Scenario 3 (Employer Co-Sponsored Transition) is optimal. Utilize employer assistance to eliminate/minimize personal financing."
        elif notice_res.shortfall_days <= 15:
            rec = "Scenario 2 (Employee-Funded Early Buyout) is recommended to protect your new job offer with minimal financial impact."
        else:
            rec = "Scenario 6 (Serve Extra 15 Days + Reduced Buyout) or Scenario 3 offers the best balance of cost savings and relationship management."

        return ScenarioComparisonMatrix(
            baseline_notice=notice_res,
            baseline_buyout=baseline_buyout,
            scenarios=scenarios,
            summary_recommendation=rec
        )

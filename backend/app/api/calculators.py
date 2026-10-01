from fastapi import APIRouter, HTTPException, status
from app.engines import (
    NoticePeriodCalculator,
    BuyoutCalculator,
    JoiningDateCalculator,
    RepaymentCalculator,
    ScenarioEngine
)
from app.schemas.calculation import (
    NoticeCalculationRequest,
    NoticeCalculationResponse,
    BuyoutCalculationRequest,
    BuyoutCalculationResponse,
    RepaymentCalculationRequest,
    RepaymentCalculationResponse,
    ScenarioSimulationRequest,
    ScenarioSimulationResponse
)
from app.schemas.origin import contract_derived, user_provided, calculated

router = APIRouter(tags=["Calculators & Engines"])

@router.post("/notice/calculate", response_model=NoticeCalculationResponse)
def calculate_notice(payload: NoticeCalculationRequest):
    try:
        res = NoticePeriodCalculator.calculate(
            contractual_notice_period=payload.contractual_notice_period,
            resignation_date=payload.resignation_date,
            intended_joining_date=payload.intended_joining_date,
            days_already_served=payload.days_already_served,
            leave_adjustment_days=payload.leave_adjustment_days
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return NoticeCalculationResponse(
        contractual_notice_days=contract_derived(res.contractual_notice_days, "Contract Clause"),
        days_already_served=user_provided(res.days_already_served, "Attendance/Resignation Record"),
        leave_adjustment_days=user_provided(res.leave_adjustment_days, "Leave Ledger"),
        effective_served_days=calculated(res.effective_served_days, "NoticePeriodCalculator"),
        remaining_notice_days=calculated(res.remaining_notice_days, "NoticePeriodCalculator"),
        earliest_release_date=calculated(res.earliest_release_date, "NoticePeriodCalculator"),
        intended_joining_date=user_provided(res.intended_joining_date, "Offer Start Date"),
        shortfall_days=calculated(res.shortfall_days, "NoticePeriodCalculator"),
        delay_days=calculated(res.delay_days, "NoticePeriodCalculator"),
        is_transition_feasible_without_buyout=calculated(res.is_transition_feasible_without_buyout, "NoticePeriodCalculator"),
        status_summary=res.status_summary,
        timeline=res.timeline,
        explanation=res.explanation
    )

@router.post("/buyout/calculate", response_model=BuyoutCalculationResponse)
def calculate_buyout(payload: BuyoutCalculationRequest):
    try:
        res = BuyoutCalculator.calculate(
            salary_amount=payload.salary_amount,
            remaining_days=payload.remaining_days,
            salary_basis=payload.salary_basis,
            divisor_basis=payload.divisor_basis,
            custom_divisor=payload.custom_divisor,
            employer_contribution=payload.employer_contribution,
            currency_symbol=payload.currency_symbol
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return BuyoutCalculationResponse(
        salary_basis=contract_derived(res.salary_basis.value, "Employment Agreement Annexure"),
        salary_amount=contract_derived(res.salary_amount, "Employment Agreement Annexure"),
        divisor_basis=contract_derived(res.divisor_basis.value, "Employment Agreement Clause"),
        divisor_value=contract_derived(res.divisor_value, "Divisor Calculation"),
        remaining_days=calculated(res.remaining_days, "Notice Engine Shortfall"),
        daily_rate=calculated(res.daily_rate, "BuyoutCalculator.daily_rate"),
        gross_buyout_amount=calculated(res.gross_buyout_amount, "BuyoutCalculator.gross_buyout"),
        employer_contribution=user_provided(res.employer_contribution, "New Employer Buyout Bonus"),
        net_employee_payable=calculated(res.net_employee_payable, "BuyoutCalculator.net_payable"),
        formula_used=calculated(res.formula_used, "BuyoutCalculator.formula"),
        detailed_steps=res.detailed_steps
    )

@router.post("/repayment/calculate", response_model=RepaymentCalculationResponse)
def calculate_repayment(payload: RepaymentCalculationRequest):
    try:
        res = RepaymentCalculator.calculate(
            principal=payload.principal,
            duration_months=payload.duration_months,
            annual_interest_rate_percent=payload.annual_interest_rate_percent,
            service_fee_percent=payload.service_fee_percent,
            flat_service_fee=payload.flat_service_fee
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return RepaymentCalculationResponse(
        principal_amount=user_provided(res.principal_amount, "Financing Request / Buyout Net Amount"),
        duration_months=user_provided(res.duration_months, "User Selected Tenor"),
        annual_interest_rate_percent=user_provided(res.annual_interest_rate_percent, "Simulation Rate Model"),
        total_service_fee=calculated(res.total_service_fee, "RepaymentCalculator.fees"),
        monthly_repayment_amount=calculated(res.monthly_repayment_amount, "RepaymentCalculator.amortized_emi"),
        total_interest_paid=calculated(res.total_interest_paid, "RepaymentCalculator.interest_sum"),
        total_repayment_amount=calculated(res.total_repayment_amount, "RepaymentCalculator.total_principal_and_interest"),
        total_overall_cost=calculated(res.total_overall_cost, "RepaymentCalculator.total_cost"),
        effective_cost_ratio=calculated(res.effective_cost_ratio, "RepaymentCalculator.cost_ratio"),
        amortization_schedule=res.amortization_schedule,
        formula_explanation=res.formula_explanation,
        breakdown=res.breakdown
    )

@router.post("/scenario/simulate", response_model=ScenarioSimulationResponse)
def simulate_scenarios(payload: ScenarioSimulationRequest):
    try:
        res = ScenarioEngine.simulate(
            contractual_notice_period=payload.contractual_notice_period,
            resignation_date=payload.resignation_date,
            intended_joining_date=payload.intended_joining_date,
            days_already_served=payload.days_already_served,
            leave_adjustment_days=payload.leave_adjustment_days,
            monthly_salary=payload.monthly_salary,
            gross_monthly_salary=payload.gross_monthly_salary,
            salary_basis=payload.salary_basis,
            divisor_basis=payload.divisor_basis,
            custom_divisor=payload.custom_divisor,
            employer_offered_contribution=payload.employer_offered_contribution,
            preferred_tenor_months=payload.preferred_tenor_months,
            annual_interest_rate_percent=payload.annual_interest_rate_percent,
            service_fee_percent=payload.service_fee_percent
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return ScenarioSimulationResponse(
        baseline_notice=res.baseline_notice,
        baseline_buyout=res.baseline_buyout,
        scenarios=res.scenarios,
        summary_recommendation=res.summary_recommendation
    )

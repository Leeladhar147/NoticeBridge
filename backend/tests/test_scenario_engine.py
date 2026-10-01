from datetime import date
from app.engines.scenario_engine import ScenarioEngine
from app.engines.buyout_engine import SalaryBasis, DivisorBasis

def test_scenario_matrix_generation():
    resignation = date(2026, 1, 1)
    intended_joining = date(2026, 1, 31)  # 30 days after resignation
    
    matrix = ScenarioEngine.simulate(
        contractual_notice_period=90,
        resignation_date=resignation,
        intended_joining_date=intended_joining,
        days_already_served=30,
        leave_adjustment_days=0,
        monthly_salary=60000.0,
        gross_monthly_salary=90000.0,
        salary_basis=SalaryBasis.BASIC,
        divisor_basis=DivisorBasis.THIRTY_DAYS,
        employer_offered_contribution=30000.0,
        preferred_tenor_months=6
    )

    assert matrix.baseline_notice.contractual_notice_days == 90
    assert matrix.baseline_notice.shortfall_days == 60
    assert matrix.baseline_buyout.gross_buyout_amount == 120000.0

    # Ensure all scenarios exist
    scenario_ids = [s.id for s in matrix.scenarios]
    assert "scenario-1-full-notice" in scenario_ids
    assert "scenario-2-full-buyout" in scenario_ids
    assert "scenario-3-employer-co-pay" in scenario_ids
    assert "scenario-4-repayment-12m" in scenario_ids
    assert "scenario-5-salary-basis-variant" in scenario_ids
    assert "scenario-6-negotiated-service" in scenario_ids

    # Check Scenario 1 (Full Notice)
    s1 = next(s for s in matrix.scenarios if s.id == "scenario-1-full-notice")
    assert s1.gross_buyout_cost == 0.0
    assert s1.net_employee_liability == 0.0
    assert s1.delay_in_joining_days == 60
    assert s1.is_financially_lightest is True

    # Check Scenario 2 (Full Buyout)
    s2 = next(s for s in matrix.scenarios if s.id == "scenario-2-full-buyout")
    assert s2.gross_buyout_cost == 120000.0
    assert s2.net_employee_liability == 120000.0
    assert s2.delay_in_joining_days == 0
    assert s2.is_fastest_transition is True

    # Check Scenario 3 (Employer Co-Pay)
    s3 = next(s for s in matrix.scenarios if s.id == "scenario-3-employer-co-pay")
    assert s3.employer_contribution == 30000.0
    assert s3.net_employee_liability == 90000.0
    assert s3.delay_in_joining_days == 0

    # Check Scenario 6 (Negotiated 15 days extra)
    s6 = next(s for s in matrix.scenarios if s.id == "scenario-6-negotiated-service")
    # Reduced shortfall = 60 - 15 = 45 days. Gross = 2000 * 45 = 90000.
    assert s6.gross_buyout_cost == 90000.0
    assert s6.delay_in_joining_days == 15

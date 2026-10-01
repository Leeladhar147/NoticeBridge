import pytest
from app.engines.repayment_engine import RepaymentCalculator

def test_zero_interest_financing():
    principal = 120000.0
    duration = 6
    
    result = RepaymentCalculator.calculate(
        principal=principal,
        duration_months=duration,
        annual_interest_rate_percent=0.0,
        service_fee_percent=1.0,
        flat_service_fee=500.0
    )

    assert result.monthly_repayment_amount == 20000.0
    assert result.total_interest_paid == 0.0
    assert result.total_repayment_amount == 120000.0
    # Service fee: 1.0% of 120,000 = 1200 + 500 flat = 1700
    assert result.total_service_fee == 1700.0
    assert result.total_overall_cost == 121700.0

    # Verify amortization schedule
    assert len(result.amortization_schedule) == 6
    assert result.amortization_schedule[0].opening_balance == 120000.0
    assert result.amortization_schedule[-1].closing_balance == 0.0
    
    total_principals = sum(entry.principal_component for entry in result.amortization_schedule)
    assert round(total_principals, 2) == principal

def test_interest_bearing_amortization():
    principal = 100000.0
    duration = 12
    rate = 12.0  # 12% APR = 1% per month
    
    result = RepaymentCalculator.calculate(
        principal=principal,
        duration_months=duration,
        annual_interest_rate_percent=rate,
        service_fee_percent=0.0
    )

    # Monthly EMI for 100,000 @ 12% APR for 12 months is ~8884.88
    assert round(result.monthly_repayment_amount, 2) == 8884.88
    assert result.total_interest_paid > 0
    assert result.total_repayment_amount == round(principal + result.total_interest_paid, 2)

    # Amortization check
    assert len(result.amortization_schedule) == 12
    assert result.amortization_schedule[0].opening_balance == 100000.0
    assert result.amortization_schedule[-1].closing_balance == 0.0
    total_principal_paid = sum(item.principal_component for item in result.amortization_schedule)
    assert round(total_principal_paid, 2) == principal

def test_repayment_input_validations():
    with pytest.raises(ValueError, match="strictly positive"):
        RepaymentCalculator.calculate(principal=0, duration_months=6)

    with pytest.raises(ValueError, match="strictly positive"):
        RepaymentCalculator.calculate(principal=-1000, duration_months=6)

    with pytest.raises(ValueError, match="at least 1 month"):
        RepaymentCalculator.calculate(principal=50000, duration_months=0)

    with pytest.raises(ValueError, match="cannot be negative"):
        RepaymentCalculator.calculate(principal=50000, duration_months=6, annual_interest_rate_percent=-2.0)

    with pytest.raises(ValueError, match="cannot be negative"):
        RepaymentCalculator.calculate(principal=50000, duration_months=6, service_fee_percent=-1.0)

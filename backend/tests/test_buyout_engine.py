import pytest
from app.engines.buyout_engine import BuyoutCalculator, SalaryBasis, DivisorBasis

def test_prompt_buyout_example():
    """
    Test exact case specified in product requirements:
    Monthly applicable salary = ₹60,000
    Notice period = 90 days, Served = 30 days, Remaining = 60 days
    If contract uses 30-day monthly basis:
    ₹60,000 / 30 × 60 = ₹120,000
    """
    result = BuyoutCalculator.calculate(
        salary_amount=60000.0,
        remaining_days=60,
        salary_basis=SalaryBasis.BASIC,
        divisor_basis=DivisorBasis.THIRTY_DAYS,
        employer_contribution=0.0
    )

    assert result.salary_amount == 60000.0
    assert result.divisor_value == 30.0
    assert result.remaining_days == 60
    assert result.daily_rate == 2000.0
    assert result.gross_buyout_amount == 120000.0
    assert result.net_employee_payable == 120000.0
    assert "₹60,000.00 / 30" in result.formula_used
    assert "₹120,000.00" in result.formula_used
    assert result.salary_basis == SalaryBasis.BASIC

def test_twenty_six_working_days_basis():
    """
    Test 26-day working divisor basis (common in statutory gratuity/industrial practices).
    ₹52,000 / 26 = ₹2,000/day. For 30 days = ₹60,000.
    """
    result = BuyoutCalculator.calculate(
        salary_amount=52000.0,
        remaining_days=30,
        salary_basis=SalaryBasis.GROSS,
        divisor_basis=DivisorBasis.TWENTY_SIX_DAYS
    )

    assert result.divisor_value == 26.0
    assert result.daily_rate == 2000.0
    assert result.gross_buyout_amount == 60000.0
    assert result.salary_basis == SalaryBasis.GROSS

def test_custom_divisor():
    result = BuyoutCalculator.calculate(
        salary_amount=50000.0,
        remaining_days=10,
        divisor_basis=DivisorBasis.CUSTOM_DIVISOR,
        custom_divisor=25.0
    )

    assert result.divisor_value == 25.0
    assert result.daily_rate == 2000.0
    assert result.gross_buyout_amount == 20000.0

def test_annual_365_divisor():
    # Monthly salary 30,000. Divisor = 365 / 12 = 30.416666...
    # Daily rate = 30000 / 30.416667 = 986.3014
    result = BuyoutCalculator.calculate(
        salary_amount=30000.0,
        remaining_days=15,
        divisor_basis=DivisorBasis.ANNUAL_365
    )

    expected_daily = round((30000.0 * 12.0) / 365.0, 4)
    assert abs(result.daily_rate - expected_daily) < 0.01
    assert result.gross_buyout_amount > 0

def test_employer_contribution_offsets():
    # Buyout: ₹120,000
    # Employer offers ₹50,000 assistance
    # Net payable by employee: ₹70,000
    result = BuyoutCalculator.calculate(
        salary_amount=60000.0,
        remaining_days=60,
        employer_contribution=50000.0
    )

    assert result.gross_buyout_amount == 120000.0
    assert result.employer_contribution == 50000.0
    assert result.net_employee_payable == 70000.0

def test_employer_contribution_exceeds_buyout():
    # Buyout: ₹40,000, Employer offers ₹50,000
    # Net payable should be clamped at 0.0, not negative
    result = BuyoutCalculator.calculate(
        salary_amount=60000.0,
        remaining_days=20,
        employer_contribution=50000.0
    )

    assert result.gross_buyout_amount == 40000.0
    assert result.net_employee_payable == 0.0

def test_zero_remaining_days():
    result = BuyoutCalculator.calculate(
        salary_amount=60000.0,
        remaining_days=0
    )
    assert result.gross_buyout_amount == 0.0
    assert result.net_employee_payable == 0.0

def test_zero_or_negative_salary_raises_error():
    with pytest.raises(ValueError, match="strictly positive"):
        BuyoutCalculator.calculate(
            salary_amount=0.0,
            remaining_days=30
        )

    with pytest.raises(ValueError, match="strictly positive"):
        BuyoutCalculator.calculate(
            salary_amount=-5000.0,
            remaining_days=30
        )

def test_negative_remaining_days_raises_error():
    with pytest.raises(ValueError, match="cannot be negative"):
        BuyoutCalculator.calculate(
            salary_amount=50000.0,
            remaining_days=-10
        )

def test_invalid_custom_divisor():
    with pytest.raises(ValueError, match="Custom divisor must be positive"):
        BuyoutCalculator.calculate(
            salary_amount=50000.0,
            remaining_days=10,
            divisor_basis=DivisorBasis.CUSTOM_DIVISOR,
            custom_divisor=0
        )

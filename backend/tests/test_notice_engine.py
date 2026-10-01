import pytest
from datetime import date, timedelta
from app.engines.notice_engine import NoticePeriodCalculator, NoticeResult

def test_standard_notice_calculation():
    # Example from prompt:
    # Notice: 90 days, Resignation: 2026-01-01, Intended Joining: 2026-01-31 (30 days later)
    # Days served: 30, Remaining: 60, Shortfall: 60
    resignation = date(2026, 1, 1)
    intended_joining = date(2026, 1, 31)
    
    result = NoticePeriodCalculator.calculate(
        contractual_notice_period=90,
        resignation_date=resignation,
        intended_joining_date=intended_joining,
        days_already_served=30,
        leave_adjustment_days=0
    )

    assert result.contractual_notice_days == 90
    assert result.days_already_served == 30
    assert result.remaining_notice_days == 60
    assert result.shortfall_days == 60
    assert result.delay_days == 60
    assert result.earliest_release_date == resignation + timedelta(days=90)
    assert result.is_transition_feasible_without_buyout is False
    assert len(result.timeline) == 4

def test_leave_adjustment_reduces_remaining_and_release_date():
    resignation = date(2026, 1, 1)
    intended_joining = date(2026, 3, 2)  # 60 days after resignation
    
    result = NoticePeriodCalculator.calculate(
        contractual_notice_period=90,
        resignation_date=resignation,
        intended_joining_date=intended_joining,
        days_already_served=30,
        leave_adjustment_days=10  # 10 accrued leave days applied to notice
    )

    # Effective served = 30 + 10 = 40 days
    # Remaining = 90 - 40 = 50 days
    # Earliest release = Jan 1 + (90 - 10) = 80 days
    assert result.effective_served_days == 40
    assert result.remaining_notice_days == 50
    assert result.earliest_release_date == resignation + timedelta(days=80)

def test_seamless_transition_when_joining_after_release():
    resignation = date(2026, 1, 1)
    # Full notice = 30 days. Release date = 2026-01-31. Intended joining = 2026-02-15
    intended_joining = date(2026, 2, 15)

    result = NoticePeriodCalculator.calculate(
        contractual_notice_period=30,
        resignation_date=resignation,
        intended_joining_date=intended_joining,
        days_already_served=15
    )

    assert result.shortfall_days == 0
    assert result.delay_days == 0
    assert result.is_transition_feasible_without_buyout is True
    assert "buffer" in result.status_summary.lower()

def test_exact_release_date_match():
    resignation = date(2026, 1, 1)
    intended_joining = resignation + timedelta(days=60)

    result = NoticePeriodCalculator.calculate(
        contractual_notice_period=60,
        resignation_date=resignation,
        intended_joining_date=intended_joining,
        days_already_served=0
    )

    assert result.shortfall_days == 0
    assert result.is_transition_feasible_without_buyout is True

def test_zero_or_negative_contractual_notice_raises_error():
    resignation = date(2026, 1, 1)
    intended_joining = date(2026, 2, 1)

    with pytest.raises(ValueError, match="must be positive"):
        NoticePeriodCalculator.calculate(
            contractual_notice_period=0,
            resignation_date=resignation,
            intended_joining_date=intended_joining
        )

    with pytest.raises(ValueError, match="must be positive"):
        NoticePeriodCalculator.calculate(
            contractual_notice_period=-30,
            resignation_date=resignation,
            intended_joining_date=intended_joining
        )

def test_negative_days_served_raises_error():
    resignation = date(2026, 1, 1)
    with pytest.raises(ValueError, match="cannot be negative"):
        NoticePeriodCalculator.calculate(
            contractual_notice_period=60,
            resignation_date=resignation,
            intended_joining_date=date(2026, 3, 1),
            days_already_served=-5
        )

def test_days_served_exceeding_notice_raises_error():
    resignation = date(2026, 1, 1)
    with pytest.raises(ValueError, match="cannot exceed contractual notice"):
        NoticePeriodCalculator.calculate(
            contractual_notice_period=30,
            resignation_date=resignation,
            intended_joining_date=date(2026, 3, 1),
            days_already_served=45
        )

def test_intended_joining_before_resignation_raises_error():
    resignation = date(2026, 5, 1)
    intended_joining = date(2026, 4, 15)  # Impossible: joining before resigning

    with pytest.raises(ValueError, match="cannot be earlier than resignation"):
        NoticePeriodCalculator.calculate(
            contractual_notice_period=60,
            resignation_date=resignation,
            intended_joining_date=intended_joining
        )

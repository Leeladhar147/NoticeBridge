from datetime import date
from app.engines.joining_engine import JoiningDateCalculator, FeasibilityStatus

def test_joining_with_shortfall():
    release = date(2026, 4, 1)
    target_join = date(2026, 3, 1)  # Required to join 31 days prior to release

    res = JoiningDateCalculator.calculate(release, target_join)
    assert res.gap_days == 31
    assert res.days_that_need_to_be_resolved == 31
    assert res.buffer_days == 0
    assert res.feasibility_status == FeasibilityStatus.NOTICE_SHORTFALL
    assert "shortfall of 31 days" in res.summary_message.lower()

def test_joining_with_perfect_match():
    release = date(2026, 4, 1)
    target_join = date(2026, 4, 1)

    res = JoiningDateCalculator.calculate(release, target_join)
    assert res.gap_days == 0
    assert res.days_that_need_to_be_resolved == 0
    assert res.buffer_days == 0
    assert res.feasibility_status == FeasibilityStatus.PERFECT_MATCH

def test_joining_with_buffer():
    release = date(2026, 3, 15)
    target_join = date(2026, 4, 1)  # 17 days buffer

    res = JoiningDateCalculator.calculate(release, target_join)
    assert res.gap_days == -17
    assert res.days_that_need_to_be_resolved == 0
    assert res.buffer_days == 17
    assert res.feasibility_status == FeasibilityStatus.FEASIBLE_WITH_BUFFER

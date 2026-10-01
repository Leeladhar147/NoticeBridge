from datetime import date
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class FeasibilityStatus(str, Enum):
    FEASIBLE_WITH_BUFFER = "feasible_with_buffer"
    PERFECT_MATCH = "perfect_match"
    NOTICE_SHORTFALL = "notice_shortfall"
    EXTENDED_GAP = "extended_gap"

class JoiningResult(BaseModel):
    earliest_possible_release_date: date
    required_joining_date: date
    gap_days: int
    days_that_need_to_be_resolved: int
    buffer_days: int
    feasibility_status: FeasibilityStatus
    summary_message: str
    recommended_action: str
    diagnostics: Dict[str, Any]

class JoiningDateCalculator:
    """
    Deterministic Joining Date and Release Synchronization Calculator.
    Calculates exact gap, days requiring contractual resolution,
    and transition feasibility.
    """

    @staticmethod
    def calculate(
        earliest_possible_release_date: date,
        required_joining_date: date
    ) -> JoiningResult:
        # gap = (earliest_possible_release_date - required_joining_date).days
        # If gap > 0: release date is later than joining date -> shortfall exists.
        # If gap == 0: release date is on the exact joining date -> seamless transition.
        # If gap < 0: release date is earlier than joining date -> candidate has a vacation/prep buffer.
        raw_gap = (earliest_possible_release_date - required_joining_date).days

        if raw_gap > 0:
            days_to_resolve = raw_gap
            buffer_days = 0
            feasibility_status = FeasibilityStatus.NOTICE_SHORTFALL
            summary = (
                f"Notice shortfall of {days_to_resolve} days. Current employer's standard release is "
                f"{earliest_possible_release_date.isoformat()}, but new employer requires joining on "
                f"{required_joining_date.isoformat()}."
            )
            recommended_action = (
                f"Resolve {days_to_resolve} days shortfall via contractual notice buyout, "
                f"or negotiate a delayed joining date of {earliest_possible_release_date.isoformat()} with new employer."
            )
        elif raw_gap == 0:
            days_to_resolve = 0
            buffer_days = 0
            feasibility_status = FeasibilityStatus.PERFECT_MATCH
            summary = "Seamless transition: Release date coincides exactly with the new joining date."
            recommended_action = "No notice buyout required. Complete standard handover and join on schedule."
        else:
            days_to_resolve = 0
            buffer_days = abs(raw_gap)
            feasibility_status = FeasibilityStatus.FEASIBLE_WITH_BUFFER
            summary = (
                f"Buffer available: Candidate is released on {earliest_possible_release_date.isoformat()}, "
                f"leaving a {buffer_days}-day rest/transition buffer before joining on {required_joining_date.isoformat()}."
            )
            recommended_action = "No notice buyout required. Candidate has ample buffer time."

        diagnostics = {
            "earliest_possible_release_date": earliest_possible_release_date.isoformat(),
            "required_joining_date": required_joining_date.isoformat(),
            "raw_gap_days": raw_gap,
            "days_to_resolve": days_to_resolve,
            "buffer_days": buffer_days,
            "status": feasibility_status.value
        }

        return JoiningResult(
            earliest_possible_release_date=earliest_possible_release_date,
            required_joining_date=required_joining_date,
            gap_days=raw_gap,
            days_that_need_to_be_resolved=days_to_resolve,
            buffer_days=buffer_days,
            feasibility_status=feasibility_status,
            summary_message=summary,
            recommended_action=recommended_action,
            diagnostics=diagnostics
        )

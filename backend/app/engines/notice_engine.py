from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class NoticeMilestone(BaseModel):
    label: str
    target_date: date
    description: str
    status: str  # "completed", "current", "target", "release"

class NoticeResult(BaseModel):
    contractual_notice_days: int
    days_already_served: int
    leave_adjustment_days: int
    effective_served_days: int
    remaining_notice_days: int
    resignation_date: date
    earliest_release_date: date
    intended_joining_date: date
    shortfall_days: int
    delay_days: int
    is_transition_feasible_without_buyout: bool
    status_summary: str
    timeline: List[NoticeMilestone]
    explanation: Dict[str, Any]

class NoticePeriodCalculator:
    """
    Deterministic Notice Period Calculator.
    Calculates served, remaining, shortfall, and release dates based purely on
    explicit contractual and calendar variables.
    """

    @staticmethod
    def calculate(
        contractual_notice_period: int,
        resignation_date: date,
        intended_joining_date: date,
        days_already_served: int = 0,
        leave_adjustment_days: int = 0
    ) -> NoticeResult:
        # Validations
        if contractual_notice_period <= 0:
            raise ValueError(f"Contractual notice period must be positive. Received: {contractual_notice_period}")
        if days_already_served < 0:
            raise ValueError(f"Days already served cannot be negative. Received: {days_already_served}")
        if leave_adjustment_days < 0:
            raise ValueError(f"Leave adjustment days cannot be negative. Received: {leave_adjustment_days}")
        if days_already_served > contractual_notice_period:
            raise ValueError(
                f"Days served ({days_already_served}) cannot exceed contractual notice ({contractual_notice_period})"
            )
        if intended_joining_date < resignation_date:
            raise ValueError(
                f"Intended joining date ({intended_joining_date}) cannot be earlier than resignation date ({resignation_date})"
            )

        # Notice math
        effective_served = days_already_served + leave_adjustment_days
        remaining_notice = max(0, contractual_notice_period - effective_served)

        # Calendar math
        # Earliest release if full remaining notice is served:
        # Full notice ends at resignation_date + contractual_notice_period.
        # Adjusted by leave credit (each leave day reduces required service days)
        full_notice_duration = max(0, contractual_notice_period - leave_adjustment_days)
        earliest_release_date = resignation_date + timedelta(days=full_notice_duration)

        # Shortfall vs intended joining date:
        # If employee leaves to join on intended_joining_date, how many notice days are left unserved?
        # Days from resignation to intended joining:
        days_until_joining = (intended_joining_date - resignation_date).days
        serviceable_before_joining = max(0, min(contractual_notice_period, days_until_joining + leave_adjustment_days))
        
        if intended_joining_date < earliest_release_date:
            shortfall_days = (earliest_release_date - intended_joining_date).days
            delay_days = shortfall_days
            is_feasible = False
            status_summary = (
                f"Notice shortfall of {shortfall_days} days. Earliest standard release is "
                f"{earliest_release_date.isoformat()}, but target joining is {intended_joining_date.isoformat()}."
            )
        else:
            shortfall_days = 0
            delay_days = 0
            is_feasible = True
            buffer_days = (intended_joining_date - earliest_release_date).days
            status_summary = (
                f"Transition is feasible without notice buyout. You have a {buffer_days}-day buffer "
                f"between release ({earliest_release_date.isoformat()}) and joining ({intended_joining_date.isoformat()})."
            )

        # Timeline representation
        timeline: List[NoticeMilestone] = [
            NoticeMilestone(
                label="Resignation Date",
                target_date=resignation_date,
                description="Formal notice served to current employer",
                status="completed" if days_already_served > 0 else "current"
            ),
            NoticeMilestone(
                label="Current Service Mark",
                target_date=resignation_date + timedelta(days=days_already_served),
                description=f"{days_already_served} days served to date",
                status="completed"
            ),
            NoticeMilestone(
                label="Earliest Release Date (Full Notice)",
                target_date=earliest_release_date,
                description=f"Standard release upon completing {contractual_notice_period} days (less {leave_adjustment_days} leave days)",
                status="release"
            ),
            NoticeMilestone(
                label="New Employer Joining Date",
                target_date=intended_joining_date,
                description="Contractual start date requested by new employer",
                status="target"
            )
        ]

        # Sort timeline by target_date
        timeline.sort(key=lambda m: m.target_date)

        explanation = {
            "contractual_notice_days": contractual_notice_period,
            "days_already_served": days_already_served,
            "leave_adjustment_days": leave_adjustment_days,
            "effective_served_days": effective_served,
            "remaining_notice_days": remaining_notice,
            "shortfall_days": shortfall_days,
            "formula_served": f"effective_served = days_already_served ({days_already_served}) + leave_adjustments ({leave_adjustment_days}) = {effective_served}",
            "formula_remaining": f"remaining_notice = max(0, contractual_notice ({contractual_notice_period}) - effective_served ({effective_served})) = {remaining_notice}",
            "formula_release": f"earliest_release_date = resignation_date ({resignation_date}) + ({contractual_notice_period} - {leave_adjustment_days}) days = {earliest_release_date}",
            "formula_shortfall": (
                f"shortfall = max(0, earliest_release_date ({earliest_release_date}) - intended_joining_date ({intended_joining_date})) = {shortfall_days} days"
                if shortfall_days > 0 else "shortfall = 0 (Intended joining is on or after release date)"
            )
        }

        return NoticeResult(
            contractual_notice_days=contractual_notice_period,
            days_already_served=days_already_served,
            leave_adjustment_days=leave_adjustment_days,
            effective_served_days=effective_served,
            remaining_notice_days=remaining_notice,
            resignation_date=resignation_date,
            earliest_release_date=earliest_release_date,
            intended_joining_date=intended_joining_date,
            shortfall_days=shortfall_days,
            delay_days=delay_days,
            is_transition_feasible_without_buyout=is_feasible,
            status_summary=status_summary,
            timeline=timeline,
            explanation=explanation,
        )

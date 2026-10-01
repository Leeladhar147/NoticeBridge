from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from .origin import TaggedValue
from app.engines.notice_engine import NoticeMilestone

class DashboardSummaryResponse(BaseModel):
    # Metric cards
    contractual_notice_period_days: TaggedValue[int]
    days_served: TaggedValue[int]
    days_remaining: TaggedValue[int]
    shortfall_days: TaggedValue[int]
    new_employer_joining_deadline: TaggedValue[Optional[date]]
    earliest_release_date: TaggedValue[Optional[date]]
    days_until_joining_deadline: TaggedValue[int]
    
    # Financial metrics
    estimated_buyout_gross: TaggedValue[float]
    employer_contribution_available: TaggedValue[float]
    financing_amount_needed: TaggedValue[float]
    repayment_estimate_monthly: TaggedValue[float]
    repayment_tenor_months: TaggedValue[int]
    
    # Status & indicators
    transition_status: TaggedValue[str]  # "Seamless", "Shortfall - Action Needed", "Buyout Financed", "On Track"
    status_tone: str  # "success", "warning", "danger", "info"
    readiness_score: int  # 0 to 100
    is_resigned: bool
    current_company: Optional[str] = None
    target_company: Optional[str] = None
    
    # Detailed visuals
    timeline_milestones: List[NoticeMilestone]
    scenario_snapshot: List[Dict[str, Any]]
    legal_disclaimer: str

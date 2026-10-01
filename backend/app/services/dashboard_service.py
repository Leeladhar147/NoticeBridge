from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.models.entities import User
from app.repositories.employee_repo import UserRepository
from app.engines import (
    NoticePeriodCalculator,
    BuyoutCalculator,
    SalaryBasis,
    DivisorBasis,
    RepaymentCalculator,
    ScenarioEngine
)
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.origin import contract_derived, user_provided, calculated
from app.config import settings

class DashboardService:
    @staticmethod
    def get_summary(db: Session, user: Optional[User] = None) -> DashboardSummaryResponse:
        """
        Builds user-specific dashboard summary from database records.
        Deterministically evaluates transition milestones, shortfall, and buyout simulations.
        """
        today = date.today()
        current_emp = None
        latest_offer = None

        if user:
            current_emp = UserRepository.get_current_employment(db, user.id)
            latest_offer = UserRepository.get_latest_offer(db, user.id)

        # If user has entered current employment and offer:
        if current_emp and latest_offer:
            current_company = current_emp.company_name
            target_company = latest_offer.company_name
            is_resigned = current_emp.is_resigned
            resignation = current_emp.resignation_date or (today - timedelta(days=30))
            target_joining = latest_offer.target_joining_date
            employer_aid = latest_offer.buyout_assistance_amount or 0.0

            contract = current_emp.contract
            notice_days = contract.notice_period_days if contract else 90
            basic_salary = contract.basic_salary_monthly if contract else 60000.0
            gross_salary = contract.gross_salary_monthly if contract and contract.gross_salary_monthly else basic_salary

            try:
                basis = SalaryBasis(contract.buyout_salary_basis) if contract else SalaryBasis.BASIC
            except Exception:
                basis = SalaryBasis.BASIC

            try:
                divisor = DivisorBasis(contract.monthly_divisor_basis) if contract else DivisorBasis.THIRTY_DAYS
            except Exception:
                divisor = DivisorBasis.THIRTY_DAYS

            # Days served
            if is_resigned and resignation and resignation <= today:
                days_served = (today - resignation).days
                days_served = min(notice_days, max(0, days_served))
            else:
                days_served = 0

            # Execute deterministic notice calculation
            notice_res = NoticePeriodCalculator.calculate(
                contractual_notice_period=notice_days,
                resignation_date=resignation,
                intended_joining_date=target_joining,
                days_already_served=days_served,
                leave_adjustment_days=0
            )

            buyout_days = notice_res.shortfall_days
            buyout_res = BuyoutCalculator.calculate(
                salary_amount=basic_salary,
                remaining_days=buyout_days,
                salary_basis=basis,
                divisor_basis=divisor,
                employer_contribution=employer_aid
            )

            principal = max(0.0, buyout_res.net_employee_payable)
            repay_res = RepaymentCalculator.calculate(
                principal=principal if principal > 0 else 1000.0,
                duration_months=6,
                annual_interest_rate_percent=10.0,
                service_fee_percent=1.0
            )

            days_until_deadline = (target_joining - today).days
            if notice_res.shortfall_days == 0:
                status = "Seamless Transition"
                tone = "success"
                readiness_score = 100
            elif employer_aid >= buyout_res.gross_buyout_amount:
                status = "100% Employer Sponsored"
                tone = "success"
                readiness_score = 95
            elif buyout_res.net_employee_payable > 0:
                status = f"Shortfall of {notice_res.shortfall_days} Days (Buyout Feasible)"
                tone = "warning"
                readiness_score = 72
            else:
                status = "Active Notice Review"
                tone = "info"
                readiness_score = 65

            scenario_matrix = ScenarioEngine.simulate(
                contractual_notice_period=notice_days,
                resignation_date=resignation,
                intended_joining_date=target_joining,
                days_already_served=days_served,
                leave_adjustment_days=0,
                monthly_salary=basic_salary,
                gross_monthly_salary=gross_salary,
                salary_basis=basis,
                divisor_basis=divisor,
                employer_offered_contribution=employer_aid,
                preferred_tenor_months=6
            )

            scenario_snapshot = [
                {
                    "id": s.id,
                    "title": s.title,
                    "tagline": s.tagline,
                    "net_cost": s.net_employee_liability,
                    "monthly_emi": s.monthly_repayment_estimate,
                    "joining_date": s.joining_date.isoformat(),
                    "delay_days": s.delay_in_joining_days,
                    "is_recommended": s.is_recommended
                }
                for s in scenario_matrix.scenarios[:4]
            ]

            return DashboardSummaryResponse(
                contractual_notice_period_days=contract_derived(notice_days, "Employment Contract Clause"),
                days_served=user_provided(days_served, "Resignation Date & Service Tracker"),
                days_remaining=calculated(notice_res.remaining_notice_days, "NoticePeriodCalculator"),
                shortfall_days=calculated(notice_res.shortfall_days, "NoticePeriodCalculator"),
                new_employer_joining_deadline=user_provided(target_joining, "New Employer Offer Letter"),
                earliest_release_date=calculated(notice_res.earliest_release_date, "NoticePeriodCalculator"),
                days_until_joining_deadline=calculated(days_until_deadline, "Calendar Math"),
                estimated_buyout_gross=calculated(buyout_res.gross_buyout_amount, "BuyoutCalculator"),
                employer_contribution_available=user_provided(employer_aid, "Offer Buyout Assistance"),
                financing_amount_needed=calculated(buyout_res.net_employee_payable, "BuyoutCalculator.net_employee_payable"),
                repayment_estimate_monthly=calculated(
                    repay_res.monthly_repayment_amount if principal > 0 else 0.0,
                    "RepaymentCalculator (6-month tenor @ 10% APR)"
                ),
                repayment_tenor_months=user_provided(6, "Simulation Configuration"),
                transition_status=calculated(status, "NoticeBridge Feasibility Logic"),
                status_tone=tone,
                readiness_score=readiness_score,
                is_resigned=is_resigned,
                current_company=current_company,
                target_company=target_company,
                timeline_milestones=notice_res.timeline,
                scenario_snapshot=scenario_snapshot,
                legal_disclaimer=settings.LEGAL_DISCLAIMER
            )

        elif current_emp and not latest_offer:
            # User added current job, waiting for offer
            current_company = current_emp.company_name
            target_company = "Target Employer Pending"
            is_resigned = current_emp.is_resigned
            resignation = current_emp.resignation_date or today
            contract = current_emp.contract
            notice_days = contract.notice_period_days if contract else 90
            basic_salary = contract.basic_salary_monthly if contract else 50000.0

            days_served = (today - resignation).days if (is_resigned and resignation <= today) else 0
            remaining = max(0, notice_days - days_served)
            earliest_release = resignation + timedelta(days=notice_days)

            return DashboardSummaryResponse(
                contractual_notice_period_days=contract_derived(notice_days, "Contract Record"),
                days_served=user_provided(days_served, "Service Tracker"),
                days_remaining=calculated(remaining, "Notice Calculator"),
                shortfall_days=calculated(0, "Awaiting New Offer"),
                new_employer_joining_deadline=user_provided(None, "Add New Offer"),
                earliest_release_date=calculated(earliest_release, "Notice Calculator"),
                days_until_joining_deadline=calculated(0, "Pending Offer Date"),
                estimated_buyout_gross=calculated(0.0, "Pending Target Date"),
                employer_contribution_available=user_provided(0.0, "Offer Assistance"),
                financing_amount_needed=calculated(0.0, "No Shortfall Yet"),
                repayment_estimate_monthly=calculated(0.0, "Repayment Engine"),
                repayment_tenor_months=user_provided(6, "Default Tenor"),
                transition_status=calculated("Offer Details Needed", "NoticeBridge Setup"),
                status_tone="info",
                readiness_score=40,
                is_resigned=is_resigned,
                current_company=current_company,
                target_company=target_company,
                timeline_milestones=[],
                scenario_snapshot=[],
                legal_disclaimer=settings.LEGAL_DISCLAIMER
            )

        else:
            # Fresh empty user state
            return DashboardSummaryResponse(
                contractual_notice_period_days=contract_derived(0, "Profile Setup"),
                days_served=user_provided(0, "Profile Setup"),
                days_remaining=calculated(0, "Profile Setup"),
                shortfall_days=calculated(0, "Profile Setup"),
                new_employer_joining_deadline=user_provided(None, "Pending Input"),
                earliest_release_date=calculated(None, "Pending Input"),
                days_until_joining_deadline=calculated(0, "Pending Input"),
                estimated_buyout_gross=calculated(0.0, "Pending Input"),
                employer_contribution_available=user_provided(0.0, "Pending Input"),
                financing_amount_needed=calculated(0.0, "Pending Input"),
                repayment_estimate_monthly=calculated(0.0, "Pending Input"),
                repayment_tenor_months=user_provided(6, "Pending Input"),
                transition_status=calculated("Profile Setup Needed", "NoticeBridge Setup"),
                status_tone="info",
                readiness_score=0,
                is_resigned=False,
                current_company=None,
                target_company=None,
                timeline_milestones=[],
                scenario_snapshot=[],
                legal_disclaimer=settings.LEGAL_DISCLAIMER
            )

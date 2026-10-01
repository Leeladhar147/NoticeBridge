from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.entities import User, CurrentEmployment, EmploymentContract, NewOffer
from app.repositories.employee_repo import UserRepository
from app.services.auth_service import get_current_user_flexible
from app.schemas.employment import (
    CurrentEmploymentCreate,
    CurrentEmploymentResponse,
    NewOfferCreate,
    NewOfferResponse
)
from app.schemas.origin import contract_derived, user_provided

router = APIRouter(prefix="/employment", tags=["Employment & Contracts"])

@router.post("/current", response_model=CurrentEmploymentResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_current_employment(
    payload: CurrentEmploymentCreate,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Creates or updates the current employment profile for the authenticated user.
    Enforces user data isolation.
    """
    employment = UserRepository.get_current_employment(db, current_user.id)
    if not employment:
        employment = CurrentEmployment(
            user_id=current_user.id,
            company_name=payload.company_name,
            designation=payload.designation,
            joining_date=payload.joining_date,
            resignation_date=payload.resignation_date,
            is_resigned=payload.is_resigned
        )
        db.add(employment)
        db.commit()
        db.refresh(employment)
        
        contract = EmploymentContract(
            current_employment_id=employment.id,
            notice_period_days=payload.notice_period_days,
            buyout_clause_permitted=payload.buyout_clause_permitted,
            buyout_salary_basis=payload.buyout_salary_basis,
            monthly_divisor_basis=payload.monthly_divisor_basis,
            custom_divisor=payload.custom_divisor,
            basic_salary_monthly=payload.basic_salary_monthly,
            gross_salary_monthly=payload.gross_salary_monthly,
            clause_reference_notes=payload.clause_reference_notes
        )
        db.add(contract)
        db.commit()
    else:
        employment.company_name = payload.company_name
        employment.designation = payload.designation
        employment.joining_date = payload.joining_date
        employment.resignation_date = payload.resignation_date
        employment.is_resigned = payload.is_resigned
        
        if not employment.contract:
            contract = EmploymentContract(
                current_employment_id=employment.id,
                notice_period_days=payload.notice_period_days,
                buyout_clause_permitted=payload.buyout_clause_permitted,
                buyout_salary_basis=payload.buyout_salary_basis,
                monthly_divisor_basis=payload.monthly_divisor_basis,
                custom_divisor=payload.custom_divisor,
                basic_salary_monthly=payload.basic_salary_monthly,
                gross_salary_monthly=payload.gross_salary_monthly,
                clause_reference_notes=payload.clause_reference_notes
            )
            db.add(contract)
        else:
            employment.contract.notice_period_days = payload.notice_period_days
            employment.contract.buyout_clause_permitted = payload.buyout_clause_permitted
            employment.contract.buyout_salary_basis = payload.buyout_salary_basis
            employment.contract.monthly_divisor_basis = payload.monthly_divisor_basis
            employment.contract.custom_divisor = payload.custom_divisor
            employment.contract.basic_salary_monthly = payload.basic_salary_monthly
            employment.contract.gross_salary_monthly = payload.gross_salary_monthly
            employment.contract.clause_reference_notes = payload.clause_reference_notes
        db.commit()
        db.refresh(employment)

    return CurrentEmploymentResponse(
        id=employment.id,
        company_name=user_provided(employment.company_name, "User Profile"),
        designation=user_provided(employment.designation, "User Profile"),
        joining_date=user_provided(employment.joining_date, "Employment History"),
        resignation_date=user_provided(employment.resignation_date, "Resignation Notice") if employment.resignation_date else None,
        is_resigned=user_provided(employment.is_resigned, "Status Check"),
        notice_period_days=contract_derived(employment.contract.notice_period_days, "Contract Clause"),
        buyout_clause_permitted=contract_derived(employment.contract.buyout_clause_permitted, "Contract Clause"),
        buyout_salary_basis=contract_derived(employment.contract.buyout_salary_basis, "Contract Clause"),
        monthly_divisor_basis=contract_derived(employment.contract.monthly_divisor_basis, "Contract Clause"),
        custom_divisor=contract_derived(employment.contract.custom_divisor, "Contract Clause") if employment.contract.custom_divisor else None,
        basic_salary_monthly=contract_derived(employment.contract.basic_salary_monthly, "Pay Annexure"),
        gross_salary_monthly=contract_derived(employment.contract.gross_salary_monthly, "Pay Annexure") if employment.contract.gross_salary_monthly else None,
        clause_reference_notes=contract_derived(employment.contract.clause_reference_notes, "Contract Clause") if employment.contract.clause_reference_notes else None,
        created_at=employment.created_at
    )

@router.get("/current", response_model=CurrentEmploymentResponse)
def get_current_employment(
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Retrieves current employment for the authenticated user."""
    employment = UserRepository.get_current_employment(db, current_user.id)
    if not employment or not employment.contract:
        raise HTTPException(status_code=404, detail="No current employment recorded for this user.")
        
    return CurrentEmploymentResponse(
        id=employment.id,
        company_name=user_provided(employment.company_name, "User Profile"),
        designation=user_provided(employment.designation, "User Profile"),
        joining_date=user_provided(employment.joining_date, "Employment History"),
        resignation_date=user_provided(employment.resignation_date, "Resignation Notice") if employment.resignation_date else None,
        is_resigned=user_provided(employment.is_resigned, "Status Check"),
        notice_period_days=contract_derived(employment.contract.notice_period_days, "Contract Clause"),
        buyout_clause_permitted=contract_derived(employment.contract.buyout_clause_permitted, "Contract Clause"),
        buyout_salary_basis=contract_derived(employment.contract.buyout_salary_basis, "Contract Clause"),
        monthly_divisor_basis=contract_derived(employment.contract.monthly_divisor_basis, "Contract Clause"),
        custom_divisor=contract_derived(employment.contract.custom_divisor, "Contract Clause") if employment.contract.custom_divisor else None,
        basic_salary_monthly=contract_derived(employment.contract.basic_salary_monthly, "Pay Annexure"),
        gross_salary_monthly=contract_derived(employment.contract.gross_salary_monthly, "Pay Annexure") if employment.contract.gross_salary_monthly else None,
        clause_reference_notes=contract_derived(employment.contract.clause_reference_notes, "Contract Clause") if employment.contract.clause_reference_notes else None,
        created_at=employment.created_at
    )

@router.post("/offer", response_model=NewOfferResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_offer(
    payload: NewOfferCreate,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Creates or updates the new employment offer for the authenticated user."""
    offer = UserRepository.get_latest_offer(db, current_user.id)
    
    if not offer:
        offer = NewOffer(
            user_id=current_user.id,
            company_name=payload.company_name,
            designation=payload.designation,
            offered_ctc_annual=payload.offered_ctc_annual,
            target_joining_date=payload.target_joining_date,
            buyout_assistance_amount=payload.buyout_assistance_amount,
            signing_bonus=payload.signing_bonus,
            retention_clawback_months=payload.retention_clawback_months
        )
        db.add(offer)
    else:
        offer.company_name = payload.company_name
        offer.designation = payload.designation
        offer.offered_ctc_annual = payload.offered_ctc_annual
        offer.target_joining_date = payload.target_joining_date
        offer.buyout_assistance_amount = payload.buyout_assistance_amount
        offer.signing_bonus = payload.signing_bonus
        offer.retention_clawback_months = payload.retention_clawback_months

    db.commit()
    db.refresh(offer)

    return NewOfferResponse(
        id=offer.id,
        company_name=user_provided(offer.company_name, "Offer Letter"),
        designation=user_provided(offer.designation, "Offer Letter"),
        offered_ctc_annual=user_provided(offer.offered_ctc_annual, "Offer Letter CTC Annexure"),
        target_joining_date=user_provided(offer.target_joining_date, "Offer Joining Date"),
        buyout_assistance_amount=user_provided(offer.buyout_assistance_amount, "Offer Buyout Assistance Clause"),
        signing_bonus=user_provided(offer.signing_bonus, "Offer Signing Bonus Clause"),
        retention_clawback_months=user_provided(offer.retention_clawback_months, "Retention Clause"),
        created_at=offer.created_at
    )

@router.get("/offer", response_model=NewOfferResponse)
def get_offer(
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Retrieves the new offer for the authenticated user."""
    offer = UserRepository.get_latest_offer(db, current_user.id)
    if not offer:
        raise HTTPException(status_code=404, detail="No new offer recorded for this user.")
        
    return NewOfferResponse(
        id=offer.id,
        company_name=user_provided(offer.company_name, "Offer Letter"),
        designation=user_provided(offer.designation, "Offer Letter"),
        offered_ctc_annual=user_provided(offer.offered_ctc_annual, "Offer Letter CTC Annexure"),
        target_joining_date=user_provided(offer.target_joining_date, "Offer Joining Date"),
        buyout_assistance_amount=user_provided(offer.buyout_assistance_amount, "Offer Buyout Assistance Clause"),
        signing_bonus=user_provided(offer.signing_bonus, "Offer Signing Bonus Clause"),
        retention_clawback_months=user_provided(offer.retention_clawback_months, "Retention Clause"),
        created_at=offer.created_at
    )

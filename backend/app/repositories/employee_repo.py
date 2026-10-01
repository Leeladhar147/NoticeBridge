from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.entities import User, CurrentEmployment, EmploymentContract, NewOffer

class UserRepository:
    """
    Data access layer for Users, Employment, and Offer records.
    Enforces user data isolation by scoping all queries to user_id.
    """

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.strip().lower()).first()

    @staticmethod
    def create_user(db: Session, name: str, email: str, password_hash: str, email_verified: bool = False) -> User:
        user = User(
            name=name.strip(),
            email=email.strip().lower(),
            password_hash=password_hash,
            email_verified=email_verified
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_current_employment(db: Session, user_id: int) -> Optional[CurrentEmployment]:
        return db.query(CurrentEmployment).filter(
            CurrentEmployment.user_id == user_id
        ).order_by(CurrentEmployment.id.desc()).first()

    @staticmethod
    def get_latest_offer(db: Session, user_id: int) -> Optional[NewOffer]:
        return db.query(NewOffer).filter(
            NewOffer.user_id == user_id
        ).order_by(NewOffer.id.desc()).first()

    @staticmethod
    def seed_demo_profile_for_user(db: Session, user: User) -> None:
        """
        Optional helper to seed sample demonstration data for a user ONLY when
        they explicitly request a demonstration walkthrough.
        """
        existing_emp = UserRepository.get_current_employment(db, user.id)
        if not existing_emp:
            today = date.today()
            resignation = today - timedelta(days=30)
            joining_current = resignation - timedelta(days=700)
            
            employment = CurrentEmployment(
                user_id=user.id,
                company_name="Apex Global Technologies",
                designation="Senior Systems Engineer",
                joining_date=joining_current,
                resignation_date=resignation,
                is_resigned=True
            )
            db.add(employment)
            db.commit()
            db.refresh(employment)

            contract = EmploymentContract(
                current_employment_id=employment.id,
                notice_period_days=90,
                buyout_clause_permitted=True,
                buyout_salary_basis="basic",
                monthly_divisor_basis="30_days",
                basic_salary_monthly=60000.0,
                gross_salary_monthly=95000.0,
                clause_reference_notes="Clause 14.2: Notice buyout permitted subject to company approval at Basic Salary rate."
            )
            db.add(contract)

            target_joining = today + timedelta(days=30)
            offer = NewOffer(
                user_id=user.id,
                company_name="HyperScale Cloud Labs",
                designation="Lead Cloud Architect",
                offered_ctc_annual=1800000.0,
                target_joining_date=target_joining,
                buyout_assistance_amount=30000.0,
                signing_bonus=50000.0,
                retention_clawback_months=12
            )
            db.add(offer)
            db.commit()


# Backward compatibility alias
EmployeeRepository = UserRepository

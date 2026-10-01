from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text,
    JSON
)
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    current_employments = relationship("CurrentEmployment", back_populates="user", cascade="all, delete-orphan")
    new_offers = relationship("NewOffer", back_populates="user", cascade="all, delete-orphan")
    notice_calculations = relationship("NoticeCalculation", back_populates="user", cascade="all, delete-orphan")
    buyout_calculations = relationship("BuyoutCalculation", back_populates="user", cascade="all, delete-orphan")
    financing_simulations = relationship("FinancingSimulation", back_populates="user", cascade="all, delete-orphan")
    scenarios = relationship("Scenario", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("UploadedDocument", back_populates="user", cascade="all, delete-orphan")

    # Compatibility properties for transitions
    @property
    def full_name(self) -> str:
        return self.name

    @full_name.setter
    def full_name(self, value: str):
        self.name = value

    @property
    def hashed_password(self) -> str:
        return self.password_hash

    @hashed_password.setter
    def hashed_password(self, value: str):
        self.password_hash = value


# Alias Employee to User for backward-compatible imports
Employee = User


class CurrentEmployment(Base):
    __tablename__ = "current_employments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=False)
    joining_date = Column(Date, nullable=False)
    resignation_date = Column(Date, nullable=True)
    is_resigned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="current_employments")
    contract = relationship("EmploymentContract", uselist=False, back_populates="employment", cascade="all, delete-orphan")

    @property
    def employee(self):
        return self.user

    @property
    def employee_id(self) -> int:
        return self.user_id

    @employee_id.setter
    def employee_id(self, val: int):
        self.user_id = val


class EmploymentContract(Base):
    __tablename__ = "employment_contracts"

    id = Column(Integer, primary_key=True, index=True)
    current_employment_id = Column(Integer, ForeignKey("current_employments.id", ondelete="CASCADE"), unique=True, nullable=False)
    notice_period_days = Column(Integer, nullable=False, default=90)  # contract-derived
    buyout_clause_permitted = Column(Boolean, default=True, nullable=False)  # contract-derived
    buyout_salary_basis = Column(String(50), default="basic", nullable=False)  # contract-derived (basic, gross, fixed, custom)
    monthly_divisor_basis = Column(String(50), default="30_days", nullable=False)  # contract-derived
    custom_divisor = Column(Float, nullable=True)  # contract-derived
    basic_salary_monthly = Column(Float, nullable=False)  # contract-derived
    gross_salary_monthly = Column(Float, nullable=True)  # contract-derived
    currency = Column(String(10), default="INR", nullable=False)  # contract-derived
    clause_reference_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    employment = relationship("CurrentEmployment", back_populates="contract")


class NewOffer(Base):
    __tablename__ = "new_offers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=False)
    offered_ctc_annual = Column(Float, nullable=False)  # user-provided
    target_joining_date = Column(Date, nullable=False)  # user-provided
    buyout_assistance_amount = Column(Float, default=0.0, nullable=False)  # user-provided / contract-derived
    signing_bonus = Column(Float, default=0.0, nullable=False)  # user-provided
    retention_clawback_months = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="new_offers")

    @property
    def employee(self):
        return self.user

    @property
    def employee_id(self) -> int:
        return self.user_id

    @employee_id.setter
    def employee_id(self, val: int):
        self.user_id = val


class NoticeCalculation(Base):
    __tablename__ = "notice_calculations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    contractual_notice_days = Column(Integer, nullable=False)  # contract-derived
    days_served = Column(Integer, nullable=False, default=0)  # user-provided
    leave_adjustment_days = Column(Integer, default=0, nullable=False)  # user-provided
    resignation_date = Column(Date, nullable=False)  # user-provided
    intended_joining_date = Column(Date, nullable=False)  # user-provided
    remaining_notice_days = Column(Integer, nullable=False)  # calculated
    earliest_release_date = Column(Date, nullable=False)  # calculated
    shortfall_days = Column(Integer, nullable=False)  # calculated
    delay_days = Column(Integer, nullable=False)  # calculated
    is_feasible_without_buyout = Column(Boolean, nullable=False)  # calculated
    metadata_provenance = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="notice_calculations")

    @property
    def employee(self):
        return self.user

    @property
    def employee_id(self) -> int:
        return self.user_id

    @employee_id.setter
    def employee_id(self, val: int):
        self.user_id = val


class BuyoutCalculation(Base):
    __tablename__ = "buyout_calculations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    salary_basis = Column(String(50), nullable=False)  # contract-derived
    applicable_monthly_salary = Column(Float, nullable=False)  # contract-derived
    divisor_basis = Column(String(50), nullable=False)  # contract-derived
    divisor_value = Column(Float, nullable=False)  # contract-derived
    remaining_days = Column(Integer, nullable=False)  # calculated / user-provided
    daily_rate = Column(Float, nullable=False)  # calculated
    gross_buyout_amount = Column(Float, nullable=False)  # calculated
    employer_contribution = Column(Float, default=0.0, nullable=False)  # user-provided
    net_employee_payable = Column(Float, nullable=False)  # calculated
    formula_used = Column(String(255), nullable=False)  # calculated
    metadata_provenance = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="buyout_calculations")

    @property
    def employee(self):
        return self.user

    @property
    def employee_id(self) -> int:
        return self.user_id

    @employee_id.setter
    def employee_id(self, val: int):
        self.user_id = val


class FinancingSimulation(Base):
    __tablename__ = "financing_simulations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    principal_amount = Column(Float, nullable=False)  # calculated / user-provided
    tenor_months = Column(Integer, nullable=False)  # user-provided
    annual_interest_rate_percent = Column(Float, nullable=False)  # user-provided / simulated
    service_fee_percent = Column(Float, default=1.5, nullable=False)  # user-provided / simulated
    total_service_fee = Column(Float, nullable=False)  # calculated
    monthly_emi = Column(Float, nullable=False)  # calculated
    total_interest_paid = Column(Float, nullable=False)  # calculated
    total_repayment_amount = Column(Float, nullable=False)  # calculated
    total_overall_cost = Column(Float, nullable=False)  # calculated
    formula_explanation = Column(Text, nullable=False)  # calculated
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="financing_simulations")
    repayment_plans = relationship("RepaymentPlan", back_populates="simulation", cascade="all, delete-orphan")

    @property
    def employee(self):
        return self.user

    @property
    def employee_id(self) -> int:
        return self.user_id

    @employee_id.setter
    def employee_id(self, val: int):
        self.user_id = val


class RepaymentPlan(Base):
    __tablename__ = "repayment_plans"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("financing_simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    month_number = Column(Integer, nullable=False)  # calculated
    opening_balance = Column(Float, nullable=False)  # calculated
    installment_amount = Column(Float, nullable=False)  # calculated
    principal_component = Column(Float, nullable=False)  # calculated
    interest_component = Column(Float, nullable=False)  # calculated
    closing_balance = Column(Float, nullable=False)  # calculated

    simulation = relationship("FinancingSimulation", back_populates="repayment_plans")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_identifier = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    scenario_type = Column(String(50), nullable=False)
    joining_date = Column(Date, nullable=False)
    gross_buyout_cost = Column(Float, nullable=False)
    net_employee_liability = Column(Float, nullable=False)
    monthly_emi = Column(Float, nullable=False)
    is_recommended = Column(Boolean, default=False, nullable=False)
    scenario_details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="scenarios")

    @property
    def employee(self):
        return self.user

    @property
    def employee_id(self) -> int:
        return self.user_id

    @employee_id.setter
    def employee_id(self, val: int):
        self.user_id = val


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, txt, md, etc.
    file_size_bytes = Column(Integer, nullable=False)
    storage_path = Column(String(512), nullable=False)
    page_count = Column(Integer, default=1, nullable=False)
    document_type = Column(String(50), default="employment_agreement", nullable=False)
    processing_status = Column(String(50), default="uploaded", nullable=False)
    extraction_results = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="documents")

    @property
    def employee(self):
        return self.user

    @property
    def employee_id(self) -> int:
        return self.user_id

    @employee_id.setter
    def employee_id(self, val: int):
        self.user_id = val

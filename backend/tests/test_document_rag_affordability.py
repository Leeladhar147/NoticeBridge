"""
Tests for NoticeBridge Document Intelligence, Targeted RAG, Anti-Hallucination Extraction,
Validation Gatekeeper, and Deterministic Affordability Simulation.
These tests run completely offline without external paid APIs.
"""

import pytest
from datetime import date
from io import BytesIO
from fastapi.testclient import TestClient

from app.main import app
from app.engines.rag_engine import TargetedRAGEngine, DocumentChunk
from app.engines.extraction_engine import ExtractionEngine
from app.engines.affordability_engine import AffordabilityCalculator
from app.services.validation_service import ExtractionValidationService
from app.schemas.intelligence import (
    ConfidenceLevel,
    ContractIntelligenceResponse,
    ExtractedSourceField,
    RetrievedClause,
    ContractConfirmationRequest,
)
from app.schemas.origin import DataOrigin

client = TestClient(app)


SAMPLE_CONTRACT_TEXT_PAGE_1 = """
EMPLOYMENT AGREEMENT
Between Acme Technologies Pvt Ltd ("Company") and Rahul Sharma ("Employee").

1. APPOINTMENT AND DESIGNATION
The Employee is appointed as Senior Software Engineer.

2. NOTICE PERIOD AND SEPARATION
Either party may terminate this employment by giving ninety (90) days notice in writing to the other party.
Such notice shall be conditional upon satisfactory handover of company assets and projects.

3. NOTICE BUYOUT AND EARLY RELEASE
In the event the Employee wishes to be relieved prior to the expiration of the stipulated ninety (90) days notice period,
the Company may, at its sole discretion, permit a notice buyout or early release.
In such event, the Employee shall be liable to pay or the Company shall recover salary in lieu of notice for the unserved
notice period calculated on the basis of Gross Monthly Salary divided by thirty (30) days.
"""

SAMPLE_CONTRACT_TEXT_PAGE_2 = """
4. COMPENSATION AND BENEFITS
The Employee shall receive the following compensation:
- Basic Salary: Rs. 60,000 per month
- House Rent Allowance: Rs. 30,000 per month
- Special Allowance: Rs. 30,000 per month
- Total Gross Salary: Rs. 120,000 per month

5. DRESS CODE AND CAFETERIA POLICY
All employees must adhere to business casual attire. The cafeteria serves meals between 12:30 PM and 2:30 PM.
"""

SAMPLE_OFFER_TEXT = """
OFFER LETTER - APEX CLOUD SYSTEMS
To: Rahul Sharma
Date: 15 October 2026

Dear Rahul,
We are pleased to offer you the position of Lead Systems Architect at Apex Cloud Systems.
Your targeted date of joining is 2026-11-15.
Annual Cost to Company (CTC) offered is Rs. 2,400,000.

TRANSITION AND NOTICE BUYOUT ASSISTANCE:
To support your seamless transition from your existing employer, Apex Cloud Systems agrees to provide
notice buyout assistance of Rs. 60,000, payable upon submission of the relieving letter.
A joining bonus of Rs. 50,000 is also approved, subject to a 12 months retention lock-in period.
"""

SAMPLE_SILENT_CONTRACT_TEXT = """
EMPLOYMENT TERMS - SILENT CORP
Employee: John Doe
Role: Associate

Clause 1: GENERAL TERMS
Employees must maintain highest ethical standards.

Clause 2: LEAVE POLICY
20 annual leaves provided per calendar year.
"""


def test_targeted_rag_clause_retrieval():
    """Test that Targeted RAG accurately retrieves notice, buyout, and salary clauses preserving page numbers."""
    pages = [
        {"page_number": 1, "text": SAMPLE_CONTRACT_TEXT_PAGE_1},
        {"page_number": 2, "text": SAMPLE_CONTRACT_TEXT_PAGE_2},
    ]
    chunks = TargetedRAGEngine.chunk_document(pages)
    assert len(chunks) >= 3

    # Notice retrieval
    notice_results = TargetedRAGEngine.retrieve_targeted_clauses(chunks, "notice_period")
    assert len(notice_results) > 0
    assert any("ninety (90) days notice" in r.evidence_text for r in notice_results)
    assert notice_results[0].page_number == 1

    # Buyout retrieval
    buyout_results = TargetedRAGEngine.retrieve_targeted_clauses(chunks, "notice_buyout")
    assert len(buyout_results) > 0
    assert any("salary in lieu of notice" in r.evidence_text for r in buyout_results)

    # Salary basis retrieval
    salary_results = TargetedRAGEngine.retrieve_targeted_clauses(chunks, "salary_basis")
    assert len(salary_results) > 0
    assert any("Gross Salary" in r.evidence_text for r in salary_results)


def test_targeted_rag_noise_filtering():
    """Test that irrelevant sections (e.g. cafeteria policy) are filtered out and not retrieved for notice/buyout queries."""
    pages = [
        {"page_number": 2, "text": SAMPLE_CONTRACT_TEXT_PAGE_2},
    ]
    chunks = TargetedRAGEngine.chunk_document(pages)
    # Searching for notice buyout in cafeteria text should return 0 results
    buyout_results = TargetedRAGEngine.retrieve_targeted_clauses(chunks, "notice_buyout", min_score=0.2)
    assert len(buyout_results) == 0


def test_contract_extraction_evidence_grounding():
    """Test that contract extraction extracts values with exact evidence quotes, pages, and high confidence."""
    pages = [
        {"page_number": 1, "text": SAMPLE_CONTRACT_TEXT_PAGE_1},
        {"page_number": 2, "text": SAMPLE_CONTRACT_TEXT_PAGE_2},
    ]
    chunks = TargetedRAGEngine.chunk_document(pages)
    extraction = ExtractionEngine.extract_contract(
        document_id=101,
        document_name="Acme_Contract.pdf",
        chunks=chunks
    )

    assert extraction.notice_period_days.value == 90
    assert extraction.notice_period_days.confidence == ConfidenceLevel.HIGH
    assert extraction.notice_period_days.page_number == 1
    assert "90" in (extraction.notice_period_days.evidence_quote or "")

    assert extraction.buyout_permitted.value is True
    assert extraction.buyout_salary_basis.value == "gross"
    assert extraction.basic_salary_monthly.value == 60000.0
    assert extraction.gross_salary_monthly.value == 120000.0


def test_anti_hallucination_on_silent_contract():
    """
    CRITICAL ANTI-HALLUCINATION TEST:
    When a contract is silent on notice buyout and salary basis,
    the AI layer MUST output UNKNOWN / Needs Confirmation and NEVER invent terms.
    """
    pages = [
        {"page_number": 1, "text": SAMPLE_SILENT_CONTRACT_TEXT},
    ]
    chunks = TargetedRAGEngine.chunk_document(pages)
    extraction = ExtractionEngine.extract_contract(
        document_id=102,
        document_name="Silent_Contract.pdf",
        chunks=chunks
    )

    # Notice buyout MUST be unknown/None
    assert extraction.buyout_permitted.value is None or extraction.buyout_permitted.confidence == ConfidenceLevel.UNKNOWN
    # Requires user confirmation MUST be True
    assert extraction.requires_user_confirmation is True
    assert len(extraction.uncertain_fields) > 0


def test_offer_extraction_and_assistance():
    """Test extraction of offer letter values, including buyout assistance and retention clawback."""
    pages = [{"page_number": 1, "text": SAMPLE_OFFER_TEXT}]
    chunks = TargetedRAGEngine.chunk_document(pages)
    offer_extraction = ExtractionEngine.extract_offer(
        document_id=201,
        document_name="Apex_Offer.pdf",
        chunks=chunks
    )

    assert "apex cloud systems" in (offer_extraction.offering_company.value or "").lower()
    assert offer_extraction.buyout_assistance_amount.value == 60000.0
    assert offer_extraction.signing_bonus.value == 50000.0
    assert offer_extraction.retention_clawback_months.value == 12


def test_validation_service_catches_contradictions_and_extremes():
    """Test validation layer rejects impossible notice periods, negative salaries, and basic > gross."""
    # 1. Contradictory salary: basic > gross
    invalid_extraction = ContractIntelligenceResponse(
        document_id=1,
        document_name="test.pdf",
        company_name=ExtractedSourceField(value="Test Co"),
        notice_period_days=ExtractedSourceField(value=90),
        notice_unit=ExtractedSourceField(value="days"),
        is_notice_conditional=ExtractedSourceField(value=False),
        notice_conditions=ExtractedSourceField(value=None),
        buyout_permitted=ExtractedSourceField(value=True),
        early_release_mentioned=ExtractedSourceField(value=True),
        buyout_salary_basis=ExtractedSourceField(value="basic"),
        monthly_divisor=ExtractedSourceField(value=30.0),
        basic_salary_monthly=ExtractedSourceField(value=100000.0),
        gross_salary_monthly=ExtractedSourceField(value=80000.0),  # Basic > Gross!
        retrieved_clauses=[],
        overall_confidence="HIGH",
        requires_user_confirmation=False,
        uncertain_fields=[]
    )
    val_result = ExtractionValidationService.validate_extracted_contract(invalid_extraction)
    assert not val_result.is_valid
    assert any("cannot exceed gross salary" in err for err in val_result.errors)

    # 2. Impossible notice period (> 365)
    invalid_extraction.basic_salary_monthly.value = 50000.0
    invalid_extraction.gross_salary_monthly.value = 80000.0
    invalid_extraction.notice_period_days.value = 720  # 720 days is invalid
    val_result2 = ExtractionValidationService.validate_extracted_contract(invalid_extraction)
    assert not val_result2.is_valid
    assert any("outside realistic bounds" in err for err in val_result2.errors)


def test_affordability_calculator_deterministic_and_neutral():
    """
    Test AffordabilityCalculator:
    - Accurate ratio percentages
    - Neutral factual wording (never 'approved', 'eligible', or credit decisions)
    - Cashflow buffer math
    """
    income = 120000.0
    obligations = 20000.0
    simulated_emi = 20000.0

    result = AffordabilityCalculator.calculate(
        new_monthly_income=income,
        existing_monthly_obligations=obligations,
        simulated_monthly_repayment=simulated_emi
    )

    # Simulated repayment = 20,000 / 120,000 = 16.67%
    assert result.repayment_income_ratio_percent.value == 16.67
    assert result.obligations_income_ratio_percent.value == 16.67
    assert result.remaining_income_after_obligations.value == 100000.0
    assert result.remaining_income_after_repayment.value == 80000.0

    # Test neutral factual statement
    assert "Your simulated repayment of ₹20,000.00 represents 16.67% of the entered monthly income" in result.factual_summary
    # Ensure forbidden credit approval wording is absent
    forbidden = ["approved", "credit approved", "eligible", "guaranteed financing", "loan approved", "ineligible"]
    for word in forbidden:
        assert word not in result.factual_summary.lower()


def test_affordability_api_endpoint():
    """Test POST /api/affordability/simulate returns valid schema and deterministic results."""
    payload = {
        "new_monthly_income": 150000.0,
        "existing_monthly_obligations": 30000.0,
        "simulated_monthly_repayment": 25000.0
    }
    response = client.post("/api/affordability/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["repayment_income_ratio_percent"]["value"] == 16.67
    assert data["remaining_income_after_repayment"]["value"] == 95000.0
    assert "factual_summary" in data
    assert data["status_tone"] in ["healthy", "moderate", "high_commitment"]


def test_document_upload_and_extraction_flow():
    """Test end-to-end document upload, RAG extraction, and user confirmation via API."""
    import uuid
    # 1. Create employee with unique email
    unique_email = f"test_{uuid.uuid4().hex[:8]}@noticebridge.io"
    emp_res = client.post("/api/auth/register", json={
        "email": unique_email,
        "full_name": "Deepika Padukone",
        "password": "Password123!"
    })
    assert emp_res.status_code == 201
    emp_id = emp_res.json()["user_id"]

    # 2. Upload text document as employment agreement
    file_bytes = SAMPLE_CONTRACT_TEXT_PAGE_1.encode("utf-8")
    files = {"file": ("Acme_Contract.txt", BytesIO(file_bytes), "text/plain")}
    data = {"employee_id": str(emp_id), "document_type": "employment_agreement"}
    upload_res = client.post("/api/documents/upload", files=files, data=data)
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["document_id"]

    # 3. Extract contract intelligence
    extract_res = client.post(f"/api/documents/{doc_id}/extract-contract")
    assert extract_res.status_code == 200
    extracted_data = extract_res.json()
    assert extracted_data["notice_period_days"]["value"] == 90
    assert extracted_data["buyout_salary_basis"]["value"] == "gross"
    assert len(extracted_data["retrieved_clauses"]) > 0

    # 4. User confirmation
    confirm_payload = {
        "document_id": doc_id,
        "company_name": "Acme Technologies",
        "notice_period_days": 90,
        "buyout_clause_permitted": True,
        "buyout_salary_basis": "gross",
        "monthly_divisor_basis": "30_days",
        "basic_salary_monthly": 60000.0,
        "gross_salary_monthly": 120000.0
    }
    confirm_res = client.post("/api/documents/confirm-contract", json=confirm_payload)
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "confirmed"

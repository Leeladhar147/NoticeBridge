"""
Document Intelligence API Router.
Handles secure upload of employment agreements & offer letters,
clause retrieval via targeted RAG, source-grounded extraction,
and human-in-the-loop confirmation before calculations.
Enforces strict user data isolation and ownership checks.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import UploadedDocument, User, EmploymentContract, CurrentEmployment
from app.schemas.intelligence import (
    ContractIntelligenceResponse,
    OfferIntelligenceResponse,
    ContractConfirmationRequest,
)
from app.services.document_service import DocumentService
from app.services.validation_service import ExtractionValidationService
from app.engines.extraction_engine import ExtractionEngine
from app.services.auth_service import get_current_user_flexible

router = APIRouter(prefix="/documents", tags=["Document Intelligence & RAG"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    employee_id: Optional[int] = Form(default=None),
    document_type: str = Form(default="employment_agreement"),
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Securely uploads an employment document (PDF, TXT, MD).
    Binds the uploaded document strictly to the authenticated user.
    Validates file type and size (<= 10MB).
    Does NOT log full document contents.
    """
    # Enforce authenticated user as document owner
    effective_user_id = current_user.id if current_user else (employee_id or 1)

    doc_service = DocumentService(db)
    doc_record = await doc_service.save_uploaded_file(
        employee_id=effective_user_id,
        file=file,
        document_type=document_type
    )

    return {
        "document_id": doc_record.id,
        "employee_id": doc_record.user_id,
        "original_filename": doc_record.original_filename,
        "file_type": doc_record.file_type,
        "file_size_bytes": doc_record.file_size_bytes,
        "page_count": doc_record.page_count,
        "document_type": doc_record.document_type,
        "processing_status": doc_record.processing_status,
        "message": f"Document '{doc_record.original_filename}' successfully uploaded and validated."
    }


@router.get("/{document_id}")
def get_document_info(
    document_id: int,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Retrieve document metadata and parsing status. Verifies user ownership."""
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if current_user and doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to view this document."
        )

    return {
        "document_id": doc.id,
        "employee_id": doc.user_id,
        "original_filename": doc.original_filename,
        "file_type": doc.file_type,
        "file_size_bytes": doc.file_size_bytes,
        "page_count": doc.page_count,
        "document_type": doc.document_type,
        "processing_status": doc.processing_status,
        "created_at": doc.created_at.isoformat() if doc.created_at else None
    }


@router.post("/{document_id}/extract-contract", response_model=ContractIntelligenceResponse)
def extract_contract_intelligence(
    document_id: int,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Performs Targeted RAG clause retrieval + Anti-Hallucination extraction
    from the uploaded current employment contract.
    Returns structured model with citations (page, section, exact quote, confidence).
    Enforces user ownership.
    """
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if current_user and doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to extract this document."
        )

    doc_service = DocumentService(db)
    chunks = doc_service.get_document_chunks(document_id)
    if not chunks:
        raise HTTPException(status_code=422, detail="Document contains no readable text content.")

    # 1. Targeted RAG retrieval & source-grounded extraction with strict anti-hallucination guardrails
    extraction = ExtractionEngine.extract_contract(
        document_id=doc.id,
        document_name=doc.original_filename,
        chunks=chunks
    )

    # 2. Validation layer check
    val_result = ExtractionValidationService.validate_extracted_contract(extraction)
    if not val_result.is_valid:
        extraction.requires_user_confirmation = True
        extraction.uncertain_fields.extend(val_result.errors)

    # Persist extraction result snapshot in document model
    doc.processing_status = "extracted"
    doc.extraction_results = extraction.model_dump(mode="json")
    db.commit()

    return extraction


@router.post("/{document_id}/extract-offer", response_model=OfferIntelligenceResponse)
def extract_offer_intelligence(
    document_id: int,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Extracts new offer letter details: new employer, role, joining date,
    compensation, and any explicitly stated buyout contribution.
    Enforces user ownership.
    """
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if current_user and doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to extract this document."
        )

    doc_service = DocumentService(db)
    chunks = doc_service.get_document_chunks(document_id)
    if not chunks:
        raise HTTPException(status_code=422, detail="Document contains no readable text content.")

    extraction = ExtractionEngine.extract_offer(
        document_id=doc.id,
        document_name=doc.original_filename,
        chunks=chunks
    )

    val_result = ExtractionValidationService.validate_extracted_offer(extraction)
    if not val_result.is_valid:
        extraction.requires_user_confirmation = True
        extraction.uncertain_fields.extend(val_result.errors)

    doc.processing_status = "extracted"
    doc.extraction_results = extraction.model_dump(mode="json")
    db.commit()

    return extraction


@router.post("/confirm-contract")
def confirm_contract_data(
    payload: ContractConfirmationRequest,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Human-in-the-loop confirmation endpoint.
    User validates or corrects uncertain values extracted from document.
    Updates the EmploymentContract in the database for deterministic calculation.
    Enforces user ownership.
    """
    is_valid, errors = ExtractionValidationService.validate_user_confirmation(payload)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"validation_errors": errors})

    doc = db.query(UploadedDocument).filter(UploadedDocument.id == payload.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if current_user and doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to confirm this document."
        )

    # Find or create employment contract for user
    current_emp = db.query(CurrentEmployment).filter(
        CurrentEmployment.user_id == doc.user_id
    ).first()

    if not current_emp:
        from datetime import date
        current_emp = CurrentEmployment(
            user_id=doc.user_id,
            company_name=payload.company_name,
            designation="Employee",
            joining_date=date.today(),
            is_resigned=False
        )
        db.add(current_emp)
        db.commit()
        db.refresh(current_emp)

    contract = db.query(EmploymentContract).filter(
        EmploymentContract.current_employment_id == current_emp.id
    ).first()

    if not contract:
        contract = EmploymentContract(
            current_employment_id=current_emp.id,
            notice_period_days=payload.notice_period_days,
            buyout_clause_permitted=payload.buyout_clause_permitted,
            buyout_salary_basis=payload.buyout_salary_basis,
            monthly_divisor_basis=payload.monthly_divisor_basis,
            custom_divisor=payload.custom_divisor,
            basic_salary_monthly=payload.basic_salary_monthly,
            gross_salary_monthly=payload.gross_salary_monthly,
            clause_reference_notes=payload.clause_reference_notes or f"Derived from {doc.original_filename}"
        )
        db.add(contract)
    else:
        contract.notice_period_days = payload.notice_period_days
        contract.buyout_clause_permitted = payload.buyout_clause_permitted
        contract.buyout_salary_basis = payload.buyout_salary_basis
        contract.monthly_divisor_basis = payload.monthly_divisor_basis
        contract.custom_divisor = payload.custom_divisor
        contract.basic_salary_monthly = payload.basic_salary_monthly
        contract.gross_salary_monthly = payload.gross_salary_monthly
        contract.clause_reference_notes = payload.clause_reference_notes or f"Derived from {doc.original_filename}"

    doc.processing_status = "confirmed"
    db.commit()

    return {
        "status": "confirmed",
        "message": "Contract parameters confirmed and saved. Ready for deterministic calculation.",
        "contract_id": contract.id,
        "notice_period_days": contract.notice_period_days,
        "buyout_clause_permitted": contract.buyout_clause_permitted,
        "buyout_salary_basis": contract.buyout_salary_basis,
        "monthly_divisor_basis": contract.monthly_divisor_basis,
        "basic_salary_monthly": contract.basic_salary_monthly,
        "gross_salary_monthly": contract.gross_salary_monthly
    }

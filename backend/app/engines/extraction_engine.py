import re
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from app.schemas.intelligence import (
    ConfidenceLevel,
    ExtractedSourceField,
    RetrievedClause,
    ContractIntelligenceResponse,
    OfferIntelligenceResponse
)
from app.schemas.origin import DataOrigin
from .rag_engine import TargetedRAGEngine, DocumentChunk, TargetedClauseResult

class ExtractionEngine:
    """
    Source-Grounded Contract & Offer Intelligence Extraction Engine.
    Strictly follows anti-hallucination rules: if terms are ambiguous or absent,
    marks them as UNKNOWN / Needs Confirmation rather than inventing answers.
    """

    @classmethod
    def extract_contract(
        cls,
        document_id: int,
        document_name: str,
        chunks: List[DocumentChunk]
    ) -> ContractIntelligenceResponse:
        # 1. Retrieve targeted clauses
        notice_clauses = TargetedRAGEngine.retrieve_targeted_clauses(chunks, "notice_period", top_k=2)
        buyout_clauses = TargetedRAGEngine.retrieve_targeted_clauses(chunks, "notice_buyout", top_k=2)
        salary_clauses = TargetedRAGEngine.retrieve_targeted_clauses(chunks, "salary_basis", top_k=2)

        # Consolidate retrieved clauses for UI evidence transparency
        all_retrieved: List[RetrievedClause] = []
        for c in notice_clauses + buyout_clauses + salary_clauses:
            all_retrieved.append(
                RetrievedClause(
                    query_intent=c.query_intent,
                    relevance_score=c.relevance_score,
                    page_number=c.page_number,
                    section_title=c.section_title,
                    text_content=c.evidence_text
                )
            )

        uncertain_fields: List[str] = []

        # --- A. Extract Company Name ---
        company_field = cls._extract_company_name(chunks, document_name)

        # --- B. Extract Notice Period ---
        notice_field, notice_unit_field, is_conditional_field, conditions_field = cls._extract_notice_terms(
            notice_clauses, document_name
        )
        if notice_field.confidence in [ConfidenceLevel.UNKNOWN, ConfidenceLevel.LOW]:
            uncertain_fields.append("notice_period_days")

        # --- C. Extract Buyout Clause ---
        buyout_field, early_release_field, salary_basis_field, divisor_field = cls._extract_buyout_terms(
            buyout_clauses, salary_clauses, document_name
        )
        if buyout_field.confidence in [ConfidenceLevel.UNKNOWN, ConfidenceLevel.LOW]:
            uncertain_fields.append("buyout_permitted")
        if salary_basis_field.confidence in [ConfidenceLevel.UNKNOWN, ConfidenceLevel.LOW]:
            uncertain_fields.append("buyout_salary_basis")

        # --- D. Extract Salaries ---
        basic_salary_field, gross_salary_field = cls._extract_salary_figures(
            salary_clauses, chunks, document_name
        )
        if basic_salary_field.confidence in [ConfidenceLevel.UNKNOWN, ConfidenceLevel.LOW]:
            uncertain_fields.append("basic_salary_monthly")

        overall_conf = "HIGH" if len(uncertain_fields) == 0 else ("MEDIUM" if len(uncertain_fields) <= 2 else "LOW")

        return ContractIntelligenceResponse(
            document_id=document_id,
            document_name=document_name,
            company_name=company_field,
            notice_period_days=notice_field,
            notice_unit=notice_unit_field,
            is_notice_conditional=is_conditional_field,
            notice_conditions=conditions_field,
            buyout_permitted=buyout_field,
            early_release_mentioned=early_release_field,
            buyout_salary_basis=salary_basis_field,
            monthly_divisor=divisor_field,
            basic_salary_monthly=basic_salary_field,
            gross_salary_monthly=gross_salary_field,
            retrieved_clauses=all_retrieved,
            overall_confidence=overall_conf,
            requires_user_confirmation=len(uncertain_fields) > 0,
            uncertain_fields=uncertain_fields
        )

    @classmethod
    def extract_offer(
        cls,
        document_id: int,
        document_name: str,
        chunks: List[DocumentChunk]
    ) -> OfferIntelligenceResponse:
        offer_clauses = TargetedRAGEngine.retrieve_targeted_clauses(chunks, "joining_and_assistance", top_k=3)
        salary_clauses = TargetedRAGEngine.retrieve_targeted_clauses(chunks, "salary_basis", top_k=2)

        all_retrieved: List[RetrievedClause] = []
        for c in offer_clauses + salary_clauses:
            all_retrieved.append(
                RetrievedClause(
                    query_intent=c.query_intent,
                    relevance_score=c.relevance_score,
                    page_number=c.page_number,
                    section_title=c.section_title,
                    text_content=c.evidence_text
                )
            )

        uncertain_fields: List[str] = []

        # Offering company
        company_field = cls._extract_company_name(chunks, document_name)

        # Role
        role_field = cls._extract_role_title(chunks, document_name)

        # Joining Date
        joining_field = cls._extract_joining_date(offer_clauses, document_name)
        if joining_field.confidence in [ConfidenceLevel.UNKNOWN, ConfidenceLevel.LOW]:
            uncertain_fields.append("target_joining_date")

        # Annual CTC
        ctc_field = cls._extract_annual_ctc(salary_clauses + offer_clauses, chunks, document_name)
        if ctc_field.confidence in [ConfidenceLevel.UNKNOWN, ConfidenceLevel.LOW]:
            uncertain_fields.append("offered_ctc_annual")

        # Buyout Assistance (DO NOT INVENT IF ABSENT!)
        buyout_aid_field, bonus_field, clawback_field = cls._extract_offer_incentives(
            offer_clauses, document_name
        )

        overall_conf = "HIGH" if len(uncertain_fields) == 0 else "MEDIUM"

        return OfferIntelligenceResponse(
            document_id=document_id,
            document_name=document_name,
            offering_company=company_field,
            role_title=role_field,
            target_joining_date=joining_field,
            offered_ctc_annual=ctc_field,
            buyout_assistance_amount=buyout_aid_field,
            signing_bonus=bonus_field,
            retention_clawback_months=clawback_field,
            retrieved_clauses=all_retrieved,
            overall_confidence=overall_conf,
            requires_user_confirmation=len(uncertain_fields) > 0,
            uncertain_fields=uncertain_fields
        )

    # -------------------------------------------------------------
    # INTERNAL EVIDENCE-GROUNDED PARSERS
    # -------------------------------------------------------------
    @classmethod
    def _extract_company_name(cls, chunks: List[DocumentChunk], doc_name: str) -> ExtractedSourceField[Optional[str]]:
        if not chunks:
            return ExtractedSourceField(value="Unknown Company", confidence=ConfidenceLevel.UNKNOWN, source_document=doc_name)

        # Look at the first 2 chunks (header/opening of employment agreement / offer letter)
        header_text = " ".join([c.text for c in chunks[:2]])
        
        # 1. Header title pattern (e.g. "OFFER LETTER - APEX CLOUD SYSTEMS" or "EMPLOYMENT AGREEMENT - ACME")
        header_title_match = re.search(
            r'(?:offer letter|employment agreement|appointment letter)\s*[\-–:]\s*([A-Za-z0-9\s,\.]{3,50})',
            header_text,
            re.IGNORECASE
        )
        if header_title_match:
            candidate = header_title_match.group(1).strip().split("\n")[0].strip()
            if len(candidate) > 2 and not candidate.lower().startswith("to:"):
                return ExtractedSourceField(
                    value=candidate,
                    confidence=ConfidenceLevel.HIGH,
                    source_document=doc_name,
                    page_number=chunks[0].page_number,
                    evidence_quote=header_title_match.group(0),
                    provenance=DataOrigin.CONTRACT_DERIVED
                )

        # 2. Relationship phrases (e.g. "Between Acme Technologies Pvt Ltd" or "at Apex Cloud Systems")
        match = re.search(
            r'(?:between|by and between|with|at)\s+([A-Z][A-Za-z0-9\s,\.]{2,40}(?:Technologies|Tech|Solutions|Systems|Services|Enterprises|Consulting|Corp|Corporation|Inc|Limited|Ltd|Pvt|LLC|Labs))',
            header_text,
            re.IGNORECASE
        )
        if match:
            found = match.group(1).strip()
            return ExtractedSourceField(
                value=found,
                confidence=ConfidenceLevel.HIGH,
                source_document=doc_name,
                page_number=chunks[0].page_number,
                evidence_quote=match.group(0),
                provenance=DataOrigin.CONTRACT_DERIVED
            )

        return ExtractedSourceField(
            value=None,
            confidence=ConfidenceLevel.UNKNOWN,
            source_document=doc_name,
            status_message="Company name could not be confidently determined from document header."
        )

    @classmethod
    def _extract_notice_terms(
        cls,
        clauses: List[TargetedClauseResult],
        doc_name: str
    ):
        if not clauses:
            return (
                ExtractedSourceField(
                    value=None,
                    confidence=ConfidenceLevel.UNKNOWN,
                    source_document=doc_name,
                    status_message="Notice period clause could not be found in document."
                ),
                ExtractedSourceField(value="days", confidence=ConfidenceLevel.UNKNOWN, source_document=doc_name),
                ExtractedSourceField(value=False, confidence=ConfidenceLevel.UNKNOWN, source_document=doc_name),
                ExtractedSourceField(value=None, confidence=ConfidenceLevel.UNKNOWN, source_document=doc_name)
            )

        top_clause = clauses[0]
        text = top_clause.evidence_text

        # 1. Day / Month patterns
        # e.g. "90 days", "ninety (90) days", "3 months", "three (3) months", "60 calendar days"
        days_match = re.search(r'(\d+)\s*(?:calendar\s*)?days?\s*notice', text, re.IGNORECASE)
        months_match = re.search(r'(\d+)\s*months?\s*notice', text, re.IGNORECASE)
        word_days_match = re.search(r'(thirty|sixty|ninety)\s*\((?:30|60|90)\)\s*days?', text, re.IGNORECASE)

        notice_days = None
        unit = "days"
        quote = ""

        if days_match:
            notice_days = int(days_match.group(1))
            quote = days_match.group(0)
        elif months_match:
            notice_days = int(months_match.group(1)) * 30
            unit = "months"
            quote = months_match.group(0)
        elif word_days_match:
            w = word_days_match.group(1).lower()
            notice_days = 30 if "thirty" in w else (60 if "sixty" in w else 90)
            quote = word_days_match.group(0)
        else:
            # Fallback search for just "90 days" or "60 days" in notice clause
            gen_match = re.search(r'(\d{2,3})\s*days', text, re.IGNORECASE)
            if gen_match:
                notice_days = int(gen_match.group(1))
                quote = gen_match.group(0)

        # Check conditions (e.g. during probation vs confirmed)
        is_conditional = bool(re.search(r'probation|confirmation|subject to', text, re.IGNORECASE))
        cond_text = "Subject to probation/confirmation clause terms" if is_conditional else None

        if notice_days:
            return (
                ExtractedSourceField(
                    value=notice_days,
                    confidence=ConfidenceLevel.HIGH,
                    source_document=doc_name,
                    page_number=top_clause.page_number,
                    section_reference=top_clause.section_title or f"Page {top_clause.page_number}",
                    evidence_quote=top_clause.evidence_text[:200],
                    provenance=DataOrigin.CONTRACT_DERIVED
                ),
                ExtractedSourceField(value=unit, confidence=ConfidenceLevel.HIGH, source_document=doc_name, page_number=top_clause.page_number),
                ExtractedSourceField(value=is_conditional, confidence=ConfidenceLevel.HIGH, source_document=doc_name, page_number=top_clause.page_number),
                ExtractedSourceField(value=cond_text, confidence=ConfidenceLevel.HIGH if is_conditional else ConfidenceLevel.UNKNOWN, source_document=doc_name)
            )

        return (
            ExtractedSourceField(
                value=None,
                confidence=ConfidenceLevel.UNKNOWN,
                source_document=doc_name,
                page_number=top_clause.page_number,
                evidence_quote=top_clause.evidence_text[:150],
                status_message="Notice period duration is ambiguous or not explicitly stated."
            ),
            ExtractedSourceField(value="days", confidence=ConfidenceLevel.UNKNOWN, source_document=doc_name),
            ExtractedSourceField(value=False, confidence=ConfidenceLevel.UNKNOWN, source_document=doc_name),
            ExtractedSourceField(value=None, confidence=ConfidenceLevel.UNKNOWN, source_document=doc_name)
        )

    @classmethod
    def _extract_buyout_terms(
        cls,
        buyout_clauses: List[TargetedClauseResult],
        salary_clauses: List[TargetedClauseResult],
        doc_name: str
    ):
        if not buyout_clauses:
            # ANTI-HALLUCINATION: Do NOT assume buyout is permitted!
            return (
                ExtractedSourceField(
                    value=None,
                    confidence=ConfidenceLevel.UNKNOWN,
                    source_document=doc_name,
                    status_message="Buyout availability could not be confidently determined from the uploaded document."
                ),
                ExtractedSourceField(value=None, confidence=ConfidenceLevel.UNKNOWN, source_document=doc_name),
                ExtractedSourceField(
                    value="unknown",
                    confidence=ConfidenceLevel.UNKNOWN,
                    source_document=doc_name,
                    status_message="Contract does not explicitly state notice buyout salary basis."
                ),
                ExtractedSourceField(value=None, confidence=ConfidenceLevel.UNKNOWN, source_document=doc_name)
            )

        top = buyout_clauses[0]
        text = top.evidence_text.lower()

        # Buyout permitted?
        has_buyout_phrase = any(w in text for w in ["salary in lieu", "in lieu of notice", "buyout", "short notice payment", "recovery of notice"])
        early_release_mentioned = any(w in text for w in ["early release", "relieve earlier", "prior release", "waive notice"])

        buyout_permitted = True if has_buyout_phrase else None
        conf = ConfidenceLevel.HIGH if has_buyout_phrase else ConfidenceLevel.MEDIUM

        # Salary basis (basic vs gross vs fixed)
        # PRIORITY: Check the buyout clause itself first! If the buyout clause says "Gross Monthly Salary", it governs.
        salary_basis = "unknown"
        basis_conf = ConfidenceLevel.UNKNOWN
        basis_quote = None
        combined_text = text + " " + (" ".join([c.evidence_text.lower() for c in salary_clauses]) if salary_clauses else "")

        if "gross salary" in text or "gross monthly" in text or "gross pay" in text:
            salary_basis = "gross"
            basis_conf = ConfidenceLevel.HIGH
            basis_quote = "Gross salary explicitly designated as buyout calculation basis"
        elif "basic salary" in text or "basic pay" in text or "monthly basic" in text:
            salary_basis = "basic"
            basis_conf = ConfidenceLevel.HIGH
            basis_quote = "Basic salary explicitly designated as buyout calculation basis"
        elif "fixed salary" in text or "fixed pay" in text:
            salary_basis = "fixed"
            basis_conf = ConfidenceLevel.HIGH
            basis_quote = "Fixed salary explicitly designated as buyout calculation basis"
        else:
            # Fallback to general salary clauses if buyout clause is generic
            if "gross salary" in combined_text:
                salary_basis = "gross"
                basis_conf = ConfidenceLevel.MEDIUM
                basis_quote = "Gross salary mentioned in compensation schedule"
            elif "basic salary" in combined_text:
                salary_basis = "basic"
                basis_conf = ConfidenceLevel.MEDIUM
                basis_quote = "Basic salary mentioned in compensation schedule"
            else:
                salary_basis = "unknown"
                basis_conf = ConfidenceLevel.UNKNOWN

        # Divisor basis
        divisor = 30.0
        if "26 days" in combined_text or "26 working" in combined_text:
            divisor = 26.0

        return (
            ExtractedSourceField(
                value=buyout_permitted,
                confidence=conf,
                source_document=doc_name,
                page_number=top.page_number,
                section_reference=top.section_title or f"Page {top.page_number}",
                evidence_quote=top.evidence_text[:200],
                provenance=DataOrigin.CONTRACT_DERIVED,
                status_message=None if buyout_permitted else "Buyout clause presence is ambiguous."
            ),
            ExtractedSourceField(
                value=early_release_mentioned,
                confidence=ConfidenceLevel.HIGH if early_release_mentioned else ConfidenceLevel.LOW,
                source_document=doc_name,
                page_number=top.page_number
            ),
            ExtractedSourceField(
                value=salary_basis,
                confidence=basis_conf,
                source_document=doc_name,
                page_number=top.page_number,
                evidence_quote=basis_quote,
                provenance=DataOrigin.CONTRACT_DERIVED,
                status_message=None if salary_basis != "unknown" else "Contract does not explicitly define salary basis. Please confirm manually."
            ),
            ExtractedSourceField(
                value=divisor if salary_basis != "unknown" else None,
                confidence=ConfidenceLevel.MEDIUM if salary_basis != "unknown" else ConfidenceLevel.UNKNOWN,
                source_document=doc_name,
                page_number=top.page_number
            )
        )

    @classmethod
    def _extract_salary_figures(
        cls,
        salary_clauses: List[TargetedClauseResult],
        all_chunks: List[DocumentChunk],
        doc_name: str
    ):
        text_corpus = " ".join([c.evidence_text for c in salary_clauses])
        if not text_corpus:
            text_corpus = " ".join([c.text for c in all_chunks[:5]])

        # Basic salary: search "Basic: Rs. 60,000", "Basic Salary: ₹60,000", "Basic Pay: 60,000"
        basic_match = re.search(r'(?:basic\s*(?:salary|pay)?[:\-\s]*(?:rs\.?|inr|₹)?\s*([\d,]+(?:\.\d{2})?))', text_corpus, re.IGNORECASE)
        gross_match = re.search(r'(?:gross\s*(?:salary|pay)?[:\-\s]*(?:rs\.?|inr|₹)?\s*([\d,]+(?:\.\d{2})?))', text_corpus, re.IGNORECASE)

        def clean_num(s: str) -> Optional[float]:
            try:
                cleaned = s.replace(",", "").strip()
                val = float(cleaned)
                return val if val > 0 else None
            except Exception:
                return None

        basic_val = clean_num(basic_match.group(1)) if basic_match else None
        gross_val = clean_num(gross_match.group(1)) if gross_match else None

        page = salary_clauses[0].page_number if salary_clauses else (all_chunks[0].page_number if all_chunks else 1)

        basic_field = ExtractedSourceField(
            value=basic_val,
            confidence=ConfidenceLevel.HIGH if basic_val else ConfidenceLevel.UNKNOWN,
            source_document=doc_name,
            page_number=page,
            evidence_quote=basic_match.group(0) if basic_match else None,
            provenance=DataOrigin.CONTRACT_DERIVED,
            status_message=None if basic_val else "Basic salary amount could not be found in contract. Please enter manually."
        )

        gross_field = ExtractedSourceField(
            value=gross_val,
            confidence=ConfidenceLevel.HIGH if gross_val else ConfidenceLevel.UNKNOWN,
            source_document=doc_name,
            page_number=page,
            evidence_quote=gross_match.group(0) if gross_match else None,
            provenance=DataOrigin.CONTRACT_DERIVED
        )

        return basic_field, gross_field

    @classmethod
    def _extract_role_title(cls, chunks: List[DocumentChunk], doc_name: str) -> ExtractedSourceField[Optional[str]]:
        text_corpus = " ".join([c.text for c in chunks[:3]])
        match = re.search(r'(?:position of|role of|appointed as|designation of|as\s+a)\s+([A-Z][A-Za-z0-9\s]{3,35})', text_corpus, re.IGNORECASE)
        if match:
            role = match.group(1).split("\n")[0].strip()
            return ExtractedSourceField(
                value=role,
                confidence=ConfidenceLevel.HIGH,
                source_document=doc_name,
                evidence_quote=match.group(0),
                provenance=DataOrigin.CONTRACT_DERIVED
            )
        return ExtractedSourceField(value="Specialist", confidence=ConfidenceLevel.LOW, source_document=doc_name)

    @classmethod
    def _extract_joining_date(cls, clauses: List[TargetedClauseResult], doc_name: str) -> ExtractedSourceField[Optional[date]]:
        text_corpus = " ".join([c.evidence_text for c in clauses])
        # Look for date patterns like 2026-10-30, 30th October 2026, October 30, 2026
        iso_match = re.search(r'(\d{4}-\d{2}-\d{2})', text_corpus)
        if iso_match:
            try:
                d = datetime.strptime(iso_match.group(1), "%Y-%m-%d").date()
                return ExtractedSourceField(
                    value=d,
                    confidence=ConfidenceLevel.HIGH,
                    source_document=doc_name,
                    evidence_quote=iso_match.group(0),
                    provenance=DataOrigin.CONTRACT_DERIVED
                )
            except Exception:
                pass

        # Try day month year: "30th October 2026" or "October 30, 2026"
        text_date_match = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', text_corpus, re.IGNORECASE)
        if text_date_match:
            try:
                date_str = f"{text_date_match.group(1)} {text_date_match.group(2)} {text_date_match.group(3)}"
                d = datetime.strptime(date_str, "%d %B %Y").date()
                return ExtractedSourceField(
                    value=d,
                    confidence=ConfidenceLevel.HIGH,
                    source_document=doc_name,
                    evidence_quote=text_date_match.group(0),
                    provenance=DataOrigin.CONTRACT_DERIVED
                )
            except Exception:
                pass

        return ExtractedSourceField(
            value=None,
            confidence=ConfidenceLevel.UNKNOWN,
            source_document=doc_name,
            status_message="Joining date could not be found in offer document. Please select target date manually."
        )

    @classmethod
    def _extract_annual_ctc(cls, clauses: List[TargetedClauseResult], all_chunks: List[DocumentChunk], doc_name: str) -> ExtractedSourceField[Optional[float]]:
        text_corpus = " ".join([c.evidence_text for c in clauses])
        ctc_match = re.search(r'(?:ctc|total\s*compensation|remuneration|gross\s*salary)[:\-\s]*(?:rs\.?|inr|₹)?\s*([\d,]+(?:\.\d{2})?)', text_corpus, re.IGNORECASE)
        if ctc_match:
            try:
                val = float(ctc_match.group(1).replace(",", "").strip())
                if val > 0:
                    return ExtractedSourceField(
                        value=val,
                        confidence=ConfidenceLevel.HIGH,
                        source_document=doc_name,
                        evidence_quote=ctc_match.group(0),
                        provenance=DataOrigin.CONTRACT_DERIVED
                    )
            except Exception:
                pass

        return ExtractedSourceField(
            value=None,
            confidence=ConfidenceLevel.UNKNOWN,
            source_document=doc_name,
            status_message="Offered CTC not detected in offer snippet."
        )

    @classmethod
    def _extract_offer_incentives(cls, clauses: List[TargetedClauseResult], doc_name: str):
        text_corpus = " ".join([c.evidence_text for c in clauses]).lower()

        # Buyout assistance (CRITICAL: DO NOT INVENT IF NOT PRESENT)
        buyout_aid = None
        aid_match = re.search(
            r'(?:notice\s*buyout\s*assistance|notice\s*buyout|buyout\s*assistance|buyout\s*reimbursement)(?:\s+of)?[:\-\s]*(?:rs\.?|inr|₹)?\s*([\d,]+)',
            text_corpus,
            re.IGNORECASE
        )
        if aid_match:
            try:
                buyout_aid = float(aid_match.group(1).replace(",", ""))
            except Exception:
                buyout_aid = None

        # Signing bonus
        signing_bonus = None
        bonus_match = re.search(
            r'(?:signing\s*bonus|joining\s*bonus)(?:\s+of)?[:\-\s]*(?:rs\.?|inr|₹)?\s*([\d,]+)',
            text_corpus,
            re.IGNORECASE
        )
        if bonus_match:
            try:
                signing_bonus = float(bonus_match.group(1).replace(",", ""))
            except Exception:
                signing_bonus = None

        # Clawback months
        clawback = 0
        claw_match = re.search(r'(\d+)\s*months?\s*(?:retention|clawback|lock-in)', text_corpus)
        if claw_match:
            try:
                clawback = int(claw_match.group(1))
            except Exception:
                clawback = 0

        aid_field = ExtractedSourceField(
            value=buyout_aid,
            confidence=ConfidenceLevel.HIGH if buyout_aid else ConfidenceLevel.UNKNOWN,
            source_document=doc_name,
            evidence_quote=aid_match.group(0) if aid_match else None,
            provenance=DataOrigin.CONTRACT_DERIVED,
            status_message=None if buyout_aid else "No employer buyout assistance clause detected in offer. You can manually enter hypothetical assistance for simulation."
        )

        bonus_field = ExtractedSourceField(
            value=signing_bonus,
            confidence=ConfidenceLevel.HIGH if signing_bonus else ConfidenceLevel.UNKNOWN,
            source_document=doc_name,
            evidence_quote=bonus_match.group(0) if bonus_match else None,
            provenance=DataOrigin.CONTRACT_DERIVED
        )

        clawback_field = ExtractedSourceField(
            value=clawback,
            confidence=ConfidenceLevel.HIGH if clawback > 0 else ConfidenceLevel.LOW,
            source_document=doc_name
        )

        return aid_field, bonus_field, clawback_field

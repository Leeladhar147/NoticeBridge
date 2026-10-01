import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DocumentChunk(BaseModel):
    chunk_id: str
    page_number: int
    section_title: Optional[str] = None
    text: str
    word_count: int

class TargetedClauseResult(BaseModel):
    query_intent: str
    chunk_id: str
    page_number: int
    section_title: Optional[str]
    evidence_text: str
    relevance_score: float
    matched_terms: List[str]

class TargetedRAGEngine:
    """
    Targeted Retrieval Engine for unstructured employment agreements and offer letters.
    Preserves exact page numbers, section references, and contextual clause boundaries.
    """

    QUERY_INTENTS = {
        "notice_period": [
            "notice period", "termination notice", "resignation notice",
            "days notice", "months notice", "written notice", "contractual notice"
        ],
        "notice_buyout": [
            "notice buyout", "salary in lieu of notice", "in lieu of notice",
            "early release", "shortfall recovery", "buyout permitted", "pay in lieu"
        ],
        "salary_basis": [
            "basic salary", "gross salary", "fixed salary", "monthly basic",
            "salary basis", "cost to company", "annexure a", "monthly compensation"
        ],
        "joining_and_assistance": [
            "date of joining", "joining date", "commencement date", "reporting date",
            "buyout assistance", "signing bonus", "joining bonus", "transition support", "retention"
        ]
    }

    @classmethod
    def chunk_document(cls, pages_text: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """
        Chunks multi-page text into coherent semantic paragraphs,
        preserving page numbers and detecting section headers.
        """
        chunks: List[DocumentChunk] = []
        chunk_idx = 0

        section_pattern = re.compile(
            r'^(?:(?:clause|section|article|\d+\.|\d+\))\s*([^\n:]+)|([A-Z\s]{4,})):?',
            re.IGNORECASE | re.MULTILINE
        )

        for page in pages_text:
            page_num = page.get("page_number", 1)
            raw_text = page.get("text", "")

            # Split into paragraphs / logical clauses
            paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
            if not paragraphs:
                paragraphs = [p.strip() for p in raw_text.split("\n") if p.strip()]

            current_section = None
            for p in paragraphs:
                sec_match = section_pattern.search(p)
                if sec_match:
                    current_section = p.split("\n")[0][:80].strip()

                words = p.split()
                if len(words) >= 5:  # filter negligible noise
                    chunk_idx += 1
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"p{page_num}_c{chunk_idx}",
                            page_number=page_num,
                            section_title=current_section,
                            text=p,
                            word_count=len(words)
                        )
                    )

        return chunks

    @classmethod
    def retrieve_targeted_clauses(
        cls,
        chunks: List[DocumentChunk],
        intent_category: str,
        min_score: float = 0.15,
        top_k: int = 3
    ) -> List[TargetedClauseResult]:
        """
        Searches document chunks for a specific contractual intent.
        Filters out irrelevant sections that don't meet minimum relevance threshold.
        """
        keywords = cls.QUERY_INTENTS.get(intent_category, [intent_category.lower()])
        results: List[TargetedClauseResult] = []

        for chunk in chunks:
            text_lower = chunk.text.lower()
            matched: List[str] = []
            score = 0.0

            for kw in keywords:
                if kw in text_lower:
                    matched.append(kw)
                    # Exact phrase matches get high weight
                    score += 1.0
                    # Proximity boost if keyword is near numbers (e.g. "90 days", "30 days", "basic salary")
                    if any(num_word in text_lower for num_word in ["days", "months", "salary", "in lieu", "basic", "gross"]):
                        score += 0.5

            if matched:
                # Normalize score by word density
                norm_score = min(1.0, round(score / (1.0 + (chunk.word_count / 100.0)), 3))
                if norm_score >= min_score:
                    results.append(
                        TargetedClauseResult(
                            query_intent=intent_category,
                            chunk_id=chunk.chunk_id,
                            page_number=chunk.page_number,
                            section_title=chunk.section_title,
                            evidence_text=chunk.text,
                            relevance_score=norm_score,
                            matched_terms=matched
                        )
                    )

        # Sort by relevance score descending
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:top_k]

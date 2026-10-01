"""
Document Service for NoticeBridge.
Manages secure upload, PDF text extraction preserving page boundaries,
storage hygiene, and document chunk preparation for RAG retrieval.
"""

import os
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from pypdf import PdfReader

from app.models.entities import UploadedDocument
from app.engines.rag_engine import TargetedRAGEngine, DocumentChunk

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "uploads"


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def validate_upload(file: UploadFile) -> Tuple[str, str]:
        """Validates extension and returns (original_name, ext)"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Uploaded file has no filename.")

        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Only PDF, TXT, and MD files are permitted."
            )
        return file.filename, ext

    async def save_uploaded_file(
        self,
        employee_id: int,
        file: UploadFile,
        document_type: str = "employment_agreement"
    ) -> UploadedDocument:
        """
        Saves file to secure local directory with a randomized UUID filename,
        validates file size, extracts page count, and creates database record.
        """
        original_name, ext = self.validate_upload(file)

        # Generate unique storage filename
        stored_name = f"{uuid.uuid4().hex}{ext}"
        target_path = UPLOAD_DIR / stored_name

        total_bytes = 0
        try:
            with open(target_path, "wb") as buffer:
                while chunk := await file.read(1024 * 64):  # 64KB chunks
                    total_bytes += len(chunk)
                    if total_bytes > MAX_FILE_SIZE_BYTES:
                        raise HTTPException(
                            status_code=413,
                            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
                        )
                    buffer.write(chunk)
        except Exception as e:
            if target_path.exists():
                try:
                    target_path.unlink()
                except OSError:
                    pass
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Failed to securely save document: {str(e)}")

        # Extract page count
        page_count = 1
        if ext == ".pdf":
            try:
                reader = PdfReader(str(target_path))
                page_count = max(1, len(reader.pages))
            except Exception:
                page_count = 1

        doc_record = UploadedDocument(
            user_id=employee_id,
            original_filename=original_name,
            stored_filename=stored_name,
            file_type=ext.replace(".", ""),
            file_size_bytes=total_bytes,
            storage_path=str(target_path),
            page_count=page_count,
            document_type=document_type,
            processing_status="uploaded"
        )
        self.db.add(doc_record)
        self.db.commit()
        self.db.refresh(doc_record)
        return doc_record

    def extract_document_pages(self, document_id: int) -> List[Tuple[int, str]]:
        """
        Extracts raw text page by page from the document.
        Returns list of (page_number, page_text).
        Does NOT log raw text to protect confidentiality.
        """
        doc = self.db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        path = Path(doc.storage_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail="Underlying document file not found on disk.")

        pages: List[Tuple[int, str]] = []
        ext = path.suffix.lower()

        if ext == ".pdf":
            try:
                reader = PdfReader(str(path))
                for page_idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    pages.append((page_idx + 1, text))
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"Failed to extract text from PDF: {str(e)}")
        else:
            # Plain text / Markdown
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                pages.append((1, content))
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"Failed to read text file: {str(e)}")

        return pages

    def get_document_chunks(self, document_id: int) -> List[DocumentChunk]:
        """
        Prepares structured DocumentChunk list for Targeted RAG indexing.
        Preserves page numbers and section boundaries.
        """
        pages = self.extract_document_pages(document_id)
        chunks: List[DocumentChunk] = []

        chunk_counter = 1
        for page_num, page_text in pages:
            # Chunk by paragraphs or double newlines
            raw_paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
            
            for para_idx, para in enumerate(raw_paragraphs):
                # Infer section header if paragraph starts with uppercase title or numbered clause
                section_title = f"Page {page_num} Clause {para_idx + 1}"
                first_line = para.split("\n")[0]
                if len(first_line) < 80 and any(kw in first_line.lower() for kw in ["clause", "section", "article", "notice", "probation", "termination", "remuneration", "compensation"]):
                    section_title = first_line.strip()

                chunk = DocumentChunk(
                    chunk_id=f"doc_{document_id}_p{page_num}_c{chunk_counter}",
                    page_number=page_num,
                    section_title=section_title,
                    text=para,
                    word_count=len(para.split())
                )
                chunks.append(chunk)
                chunk_counter += 1

        return chunks

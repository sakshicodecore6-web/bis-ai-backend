# routers/audit_routes.py
import json
import re
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel import Session

import pdfplumber
import pytesseract
from PIL import Image
import io

from database import get_session
from models import User, DocumentAuditResult
from schemas import DocumentAuditResponse, AuditFinding
from auth import get_current_user
from audit_checklist import CHECKLIST

# Point pytesseract at the actual installed engine
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

router = APIRouter(prefix="/audit", tags=["audit"])


def extract_text(file_bytes: bytes, filename: str) -> str:
    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    if lower_name.endswith((".png", ".jpg", ".jpeg")):
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(image)

    raise HTTPException(
        status_code=400,
        detail="Unsupported file type. Please upload a PDF, PNG, or JPG.",
    )


@router.post("/check", response_model=DocumentAuditResponse)
def audit_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    file_bytes = file.file.read()
    extracted_text = extract_text(file_bytes, file.filename)
    text_lower = extracted_text.lower()

    findings = []
    passed_count = 0

    for item in CHECKLIST:
        found = any(keyword in text_lower for keyword in item["keywords"])
        if not found and "regex" in item:
            found = bool(re.search(item["regex"], extracted_text, re.IGNORECASE))
        if found:
            findings.append(
                AuditFinding(status="pass", message=f"{item['label']} available")
            )
            passed_count += 1
        else:
            findings.append(
                AuditFinding(status="missing", message=f"{item['label']} missing")
            )

    readiness_score = round((passed_count / len(CHECKLIST)) * 10)

    # Save the audit result
    result = DocumentAuditResult(
        user_id=current_user.id,
        filename=file.filename,
        readiness_score=readiness_score,
        findings_json=json.dumps([f.model_dump() for f in findings]),
    )
    session.add(result)
    session.commit()

    return DocumentAuditResponse(
        filename=file.filename,
        readiness_score=readiness_score,
        findings=findings,
    )
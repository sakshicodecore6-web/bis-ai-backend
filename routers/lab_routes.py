# routers/lab_routes.py

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy import func
from database import get_session
from models import User, Laboratory
from schemas import LabMatchRequest, LabMatchResponse, LabResult
from auth import get_current_user

router = APIRouter(prefix="/labs", tags=["labs"])


@router.post("/match", response_model=LabMatchResponse)
def match_labs(
    payload: LabMatchRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    query = select(Laboratory).where(
        func.lower(Laboratory.category) == payload.category.lower()
    )

    if payload.location:
        query = query.where(
            func.lower(Laboratory.location) == payload.location.lower()
        )

    labs = session.exec(query).all()

    results = [
        LabResult(
            id=lab.id,
            name=lab.name,
            category=lab.category,
            location=lab.location,
            capability=lab.capability,
            contact_email=lab.contact_email,
            contact_phone=lab.contact_phone,
        )
        for lab in labs
    ]

    return LabMatchResponse(results=results)
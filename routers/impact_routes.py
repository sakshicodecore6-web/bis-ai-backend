# routers/impact_routes.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from database import get_session
from models import User, UserProduct, StandardChangeEvent
from schemas import (
    ImpactCheckRequest,
    ImpactCheckResponse,
    AffectedProduct,
    ChangeEventOut,
    ChangeEventListResponse,
)
from auth import get_current_user

router = APIRouter(prefix="/impact", tags=["impact"])


@router.get("/recent", response_model=ChangeEventListResponse)
def get_recent_changes(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    events = session.exec(
        select(StandardChangeEvent).order_by(StandardChangeEvent.created_at.desc())
    ).all()

    return ChangeEventListResponse(
        events=[
            ChangeEventOut(
                id=e.id,
                standard_code=e.standard_code,
                change_type=e.change_type,
                description=e.description,
                recommended_action=e.recommended_action,
            )
            for e in events
        ]
    )


@router.post("/check", response_model=ImpactCheckResponse)
def check_impact(
    payload: ImpactCheckRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Read-only lookup — this does NOT create a new StandardChangeEvent.
    # The event already exists (created via /impact/recent's data, or a
    # seed script); this endpoint just checks it against this user's products.
    affected = session.exec(
        select(UserProduct).where(
            UserProduct.user_id == current_user.id,
            UserProduct.standard_code == payload.standard_code,
        )
    ).all()

    affected_products = [
        AffectedProduct(
            product_name=p.product_name,
            category=p.category,
            standard_code=p.standard_code,
        )
        for p in affected
    ]

    return ImpactCheckResponse(
        standard_code=payload.standard_code,
        change_type=payload.change_type,
        description=payload.description,
        recommended_action=payload.recommended_action,
        affected_products=affected_products,
    )
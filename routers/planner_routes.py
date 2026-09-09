# routers/planner_routes.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from database import get_session
from models import User, PlannerProgress
from schemas import (
    PlannerInputs,
    RoadmapResponse,
    RoadmapStep,
    ProgressToggle,
    ProgressResponse,
    ProgressItem,
)
from roadmap_data import ROADMAP_STEPS
from auth import get_current_user

router = APIRouter(prefix="/planner", tags=["planner"])


@router.post("/generate", response_model=RoadmapResponse)
def generate_roadmap(
    inputs: PlannerInputs,
    current_user: User = Depends(get_current_user),
):
    # Mock/generalized logic for now — inputs aren't used to change the
    # roadmap yet, but the endpoint accepts them so the frontend contract
    # is already correct for when Hrutvik's real AI logic replaces this.
    steps = [RoadmapStep(**step) for step in ROADMAP_STEPS]
    return RoadmapResponse(steps=steps)


@router.get("/progress", response_model=ProgressResponse)
def get_progress(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    rows = session.exec(
        select(PlannerProgress).where(PlannerProgress.user_id == current_user.id)
    ).all()

    progress = [
        ProgressItem(step_id=row.step_id, is_checked=row.is_checked) for row in rows
    ]
    return ProgressResponse(progress=progress)


@router.post("/progress", response_model=ProgressResponse)
def toggle_progress(
    payload: ProgressToggle,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Look for an existing progress row for this user + step
    existing = session.exec(
        select(PlannerProgress).where(
            PlannerProgress.user_id == current_user.id,
            PlannerProgress.step_id == payload.step_id,
        )
    ).first()

    if existing:
        existing.is_checked = not existing.is_checked
        session.add(existing)
    else:
        # First time this step's been touched — create it as checked
        existing = PlannerProgress(
            user_id=current_user.id,
            step_id=payload.step_id,
            is_checked=True,
        )
        session.add(existing)

    session.commit()

    # Return the user's full updated progress list
    rows = session.exec(
        select(PlannerProgress).where(PlannerProgress.user_id == current_user.id)
    ).all()
    progress = [
        ProgressItem(step_id=row.step_id, is_checked=row.is_checked) for row in rows
    ]
    return ProgressResponse(progress=progress)

@router.get("/whoami")
def whoami(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}
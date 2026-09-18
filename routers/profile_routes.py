from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from database import get_session
from models import User, BISyncProfile
from schemas import ProfileUpdate, ProfileResponse
from auth import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    profile = session.exec(
        select(BISyncProfile).where(
            BISyncProfile.user_id == current_user.id
        )
    ).first()

    if not profile:
        profile = BISyncProfile(user_id=current_user.id)
        session.add(profile)
        session.commit()
        session.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        company_name=profile.company_name,
        manufacturer_type=profile.manufacturer_type,
        factory_location=profile.factory_location,
        business_type=profile.business_type,
    )


@router.put("", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    profile = session.exec(
        select(BISyncProfile).where(
            BISyncProfile.user_id == current_user.id
        )
    ).first()

    if not profile:
        profile = BISyncProfile(user_id=current_user.id)
        session.add(profile)

    profile.company_name = payload.company_name
    profile.manufacturer_type = payload.manufacturer_type
    profile.factory_location = payload.factory_location
    profile.business_type = payload.business_type

    session.commit()
    session.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        company_name=profile.company_name,
        manufacturer_type=profile.manufacturer_type,
        factory_location=profile.factory_location,
        business_type=profile.business_type,
    )
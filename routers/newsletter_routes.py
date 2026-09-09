# routers/newsletter_routes.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from database import get_session
from models import User, NewsletterPost, UserSubscription
from schemas import (
    NewsletterFeedResponse,
    NewsletterPostOut,
    SubscriptionToggle,
    SubscriptionResponse,
)
from auth import get_current_user

router = APIRouter(prefix="/newsletter", tags=["newsletter"])


@router.get("/feed", response_model=NewsletterFeedResponse)
def get_global_feed(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    posts = session.exec(
        select(NewsletterPost).order_by(NewsletterPost.published_at.desc())
    ).all()

    return NewsletterFeedResponse(
        posts=[NewsletterPostOut(**post.model_dump()) for post in posts]
    )


@router.get("/subscribed", response_model=NewsletterFeedResponse)
def get_subscribed_feed(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    subs = session.exec(
        select(UserSubscription).where(UserSubscription.user_id == current_user.id)
    ).all()
    categories = [s.category for s in subs]

    if not categories:
        return NewsletterFeedResponse(posts=[])

    posts = session.exec(
        select(NewsletterPost)
        .where(NewsletterPost.category.in_(categories))
        .order_by(NewsletterPost.published_at.desc())
    ).all()

    return NewsletterFeedResponse(
        posts=[NewsletterPostOut(**post.model_dump()) for post in posts]
    )


@router.post("/subscribe", response_model=SubscriptionResponse)
def toggle_subscription(
    payload: SubscriptionToggle,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    existing = session.exec(
        select(UserSubscription).where(
            UserSubscription.user_id == current_user.id,
            UserSubscription.category == payload.category,
        )
    ).first()

    if existing:
        session.delete(existing)
    else:
        session.add(
            UserSubscription(user_id=current_user.id, category=payload.category)
        )

    session.commit()

    subs = session.exec(
        select(UserSubscription).where(UserSubscription.user_id == current_user.id)
    ).all()

    return SubscriptionResponse(subscribed_categories=[s.category for s in subs])
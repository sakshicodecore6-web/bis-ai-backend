# seed_impact_data.py
from sqlmodel import Session, select
from database import engine
from models import User, UserProduct, StandardChangeEvent

with Session(engine) as session:
    # Find your test user (adjust email if different)
    user = session.exec(
        select(User).where(User.email == "test@example.com")
    ).first()

    if not user:
        print("No user found with that email — check your test account email and update this script.")
    else:
        product = UserProduct(
            user_id=user.id,
            product_name="LED Bulb",
            category="Electronics",
            standard_code="IS 16102",
        )
        session.add(product)

        event = StandardChangeEvent(
            standard_code="IS 16102",
            change_type="amended",
            description="IS 16102 has been amended to update safety and performance requirements for LED lighting products.",
            recommended_action="Review your product's compliance against the amended clauses and re-test if performance parameters changed.",
        )
        session.add(event)

        session.commit()
        print(f"Seeded UserProduct (id={product.id}) and StandardChangeEvent (id={event.id}) for user {user.email}")
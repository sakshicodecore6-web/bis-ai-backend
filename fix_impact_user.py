# fix_impact_user.py
from sqlmodel import Session, select
from database import engine
from models import User, UserProduct

with Session(engine) as session:
    user = session.exec(
        select(User).where(User.email == "test@ai.com")
    ).first()

    if not user:
        print("User test@ai.com not found.")
    else:
        product = session.exec(
            select(UserProduct).where(UserProduct.id == 1)
        ).first()

        if product:
            product.user_id = user.id
            session.add(product)
            session.commit()
            print(f"Updated UserProduct id=1 to belong to user {user.email} (id={user.id})")
        else:
            print("UserProduct id=1 not found.")
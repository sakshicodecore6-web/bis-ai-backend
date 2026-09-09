# routers/product_routes.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from database import get_session
from models import User, UserProduct
from schemas import ProductCreate, ProductOut, ProductListResponse
from auth import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    products = session.exec(
        select(UserProduct).where(UserProduct.user_id == current_user.id)
    ).all()

    return ProductListResponse(
        products=[
            ProductOut(
                id=p.id,
                product_name=p.product_name,
                category=p.category,
                standard_code=p.standard_code,
            )
            for p in products
        ]
    )


@router.post("", response_model=ProductOut)
def add_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    product = UserProduct(
        user_id=current_user.id,
        product_name=payload.product_name,
        category=payload.category,
        standard_code=payload.standard_code,
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    return ProductOut(
        id=product.id,
        product_name=product.product_name,
        category=product.category,
        standard_code=product.standard_code,
    )
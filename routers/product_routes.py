# routers/product_routes.py
from fastapi import APIRouter, Depends, HTTPException
from services.bis_service import search_bis_lims, get_bis_standard_context, discover_standards
from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
from database import get_session
from models import User, UserProduct, ProductBISContext
from schemas import (
    ProductCreate,
    ProductOut,
    ProductListResponse,
    ProductBISContextUpdate,
    ProductBISContextResponse,
)
from auth import get_current_user

router = APIRouter(prefix="/products", tags=["products"])

# Localized schema to include BIS Context in the list view safely
class ProductWithContextOut(BaseModel):
    id: int
    product_name: str
    category: str
    standard_code: str
    is_title: Optional[str] = None
    is_number: Optional[str] = None
    last_verified: Optional[datetime] = None

class ExtendedProductListResponse(BaseModel):
    products: List[ProductWithContextOut]

@router.get("", response_model=ExtendedProductListResponse)
def list_products(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    products = session.exec(
        select(UserProduct).where(UserProduct.user_id == current_user.id)
    ).all()
    
    result = []
    for p in products:
        ctx = session.exec(
            select(ProductBISContext).where(ProductBISContext.user_product_id == p.id)
        ).first()
        
        result.append(
            ProductWithContextOut(
                id=p.id,
                product_name=p.product_name,
                category=p.category,
                standard_code=p.standard_code,
                is_title=ctx.is_title if ctx else None,
                is_number=ctx.is_number if ctx else None,
                last_verified=ctx.last_verified if ctx else None,
            )
        )

    return ExtendedProductListResponse(products=result)

@router.get("/discover")
def discover_product_standards(
    query: str,
    current_user: User = Depends(get_current_user),
):
    try:
        candidates = discover_standards(query)
        return {"candidates": candidates}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"BIS LIMS discovery failed: {str(e)}")


@router.post("", response_model=ProductOut)
def add_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # App-level Duplicate Check
    existing = session.exec(
        select(UserProduct).where(
            UserProduct.user_id == current_user.id,
            UserProduct.standard_code == payload.standard_code
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"You have already added {payload.standard_code} to your registry."
        )

    product = UserProduct(
        user_id=current_user.id,
        product_name=payload.product_name,
        category=payload.category,
        standard_code=payload.standard_code,
    )
    session.add(product)
    session.commit()
    session.refresh(product)

    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Enforce Ownership
    product = session.exec(
        select(UserProduct).where(
            UserProduct.id == product_id,
            UserProduct.user_id == current_user.id,
        )
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found or unauthorized")

    # Cascading delete logic safely applied
    context = session.exec(
        select(ProductBISContext).where(ProductBISContext.user_product_id == product.id)
    ).first()

    if context:
        session.delete(context)
        
    session.delete(product)
    session.commit()
    
    return {"detail": "Product successfully deleted from your registry"}

@router.get("/bis-search/{standard_code}")
def bis_search(
    standard_code: str,
    current_user: User = Depends(get_current_user),
):
    try:
        results = search_bis_lims(standard_code)

        return {
            "standard_code": standard_code,
            "source": "BIS LIMS",
            "results": results,
        }

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"BIS LIMS search failed: {str(e)}",
        )
@router.post(
    "/{product_id}/verify-bis",
    response_model=ProductBISContextResponse,
)
def verify_bis(
    product_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    product = session.exec(
        select(UserProduct).where(
            UserProduct.id == product_id,
            UserProduct.user_id == current_user.id,
        )
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    try:
        bis_data = get_bis_standard_context(
            product.standard_code
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"BIS verification failed: {str(e)}",
        )

    context = session.exec(
        select(ProductBISContext).where(
            ProductBISContext.user_product_id == product.id
        )
    ).first()

    if not context:
        context = ProductBISContext(
            user_product_id=product.id
        )
        session.add(context)

    context.is_number = bis_data["is_number"]
    context.source_url = bis_data["source_url"]
    context.last_verified = datetime.utcnow()

    session.commit()
    session.refresh(context)

    return context

@router.get(
        
    "/{product_id}/bis-context",
    response_model=ProductBISContextResponse,
)

def get_bis_context(
    product_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    product = session.exec(
        select(UserProduct).where(
            UserProduct.id == product_id,
            UserProduct.user_id == current_user.id,
        )
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    context = session.exec(
        select(ProductBISContext).where(
            ProductBISContext.user_product_id == product.id
        )
    ).first()

    if not context:
        raise HTTPException(
            status_code=404,
            detail="BIS context not verified yet",
        )

    return context


@router.put(
    "/{product_id}/bis-context",
    response_model=ProductBISContextResponse,
)
def update_bis_context(
    product_id: int,
    payload: ProductBISContextUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    product = session.exec(
        select(UserProduct).where(
            UserProduct.id == product_id,
            UserProduct.user_id == current_user.id,
        )
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    context = session.exec(
        select(ProductBISContext).where(
            ProductBISContext.user_product_id == product.id
        )
    ).first()

    if not context:
        context = ProductBISContext(user_product_id=product.id)
        session.add(context)

    context.is_number = payload.is_number
    context.is_title = payload.is_title
    context.is_year = payload.is_year
    context.superseding_standard = payload.superseding_standard
    context.bis_scheme = payload.bis_scheme
    context.regulatory_status = payload.regulatory_status
    context.source_url = payload.source_url
    context.last_verified = datetime.utcnow()

    session.commit()
    session.refresh(context)

    return context
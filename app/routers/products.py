from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.products import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductOut
from app.core.permissions import admin_required


router = APIRouter(prefix="/products", tags=["Products"])


# LIST - everyone can access
@router.get("/", response_model=list[ProductOut])
def list_products(
        q: Optional[str] = Query(None, description="search by name substring"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db)
):
    query = db.query(Product)

    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))

    products = query.offset(skip).limit(limit).all()

    return products


# GET - single product
@router.get("/{product_id}", response_model=ProductOut)
def get_product(
        product_id: int,
        db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# CREATE - admin and superadmin
@router.post('/', response_model=ProductOut, dependencies=[Depends(admin_required)], status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db)
) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# UPDATE - admin e superadmin
@router.put("/{product_id}", response_model=ProductOut, dependencies=[Depends(admin_required)])
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),

) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for filed, value in data.model_dump().items():
        setattr(product, filed, value)

    db.commit()
    db.refresh(product)

    return product


# DELETE - superadmin only
@router.delete("/{product_id}", response_model=ProductOut, dependencies=[Depends(admin_required)])
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
        "id": product.id
    }

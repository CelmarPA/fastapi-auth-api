# app/routers/products.py

"""
Products Router
---------------

This module exposes endpoints for managing products.

Features:
- Public product listing
- Product detail retrieval
- Admin-protected product creation, update and deletion

All write operations require admin or superadmin permissions.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.products import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductOut
from app.core.permissions import admin_required


router = APIRouter(prefix="/products", tags=["Products"])


# LIST - everyone can access
@router.get("/", response_model=List[ProductOut])
def list_products(
        q: Optional[str] = Query(None, description="search by name substring"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db)
) -> List[ProductOut]:
    """
    List products with optional name filtering and pagination.

    :param q: Optional substring to search in product names.
    :type q: str | None

    :param skip: Number of items to skip.
    :type skip: int

    :param limit: Maximum number of items to return.
    :type limit: int

    :param db: Active database session.
    :type db: Session

    :return: List of matching products.
    :rtype: list[ProductOut]
    """

    query = db.query(Product)

    if q:
        query = query.filter(func.lower(Product.name).like(f"%{q.lower()}%"))

    products = query.offset(skip).limit(limit).all()

    return products


# GET - single product
@router.get("/{product_id}", response_model=ProductOut)
def get_product(
        product_id: int,
        db: Session = Depends(get_db)
) -> ProductOut:
    """
    Retrieve a single product by its ID.

    :param product_id: ID of the product.
    :type product_id: int

    :param db: Active database session.
    :type db: Session

    :return: Product details if found.
    :rtype: ProductOut
    """

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
    """
    Create a new product. Admin or superadmin only.

    :param payload: Product creation data.
    :type payload: ProductCreate

    :param db: Active database session.
    :type db: Session

    :return: Newly created product.
    :rtype: Product
    """

    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# UPDATE - admin e superadmin
@router.put("/{product_id}", response_model=ProductOut, dependencies=[Depends(admin_required)])
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db)
) -> Product:
    """
    Update an existing product. Admin or superadmin only.

    :param product_id: ID of the product to update.
    :type product_id: int

    :param product_in: Fields to update.
    :type product_in: ProductUpdate

    :param db: Active database session.
    :type db: Session

    :return: Updated product.
    :rtype: Product
    """

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return product


# DELETE - superadmin only
@router.delete("/{product_id}", response_model=ProductOut, dependencies=[Depends(admin_required)])
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> ProductOut:
    """
    Delete a product. Superadmin only (enforced by admin_required + role system).

    :param product_id: ID of the product to delete.
    :type product_id: int

    :param db: Active database session.
    :type db: Session

    :return: Deleted product data.
    :rtype: ProductOut
    """

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

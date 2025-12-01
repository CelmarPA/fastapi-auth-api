# app/schemas/product_schema.py

"""
Product Schemas
---------------

Schemas used for creating, updating, and returning product information.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProductBase(BaseModel):
    """
    Base schema with common product attributes.

    :param name: Name of the product.
    :type name: str

    :param description: Detailed description of the product.
    :type description: str | None

    :param price: Monetary price of the product.
    :type price: float

    :param stock: Quantity of the product available in stock.
    :type stock: int
    """

    name: str
    description: Optional[str] = None
    price: float
    stock: int

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(ProductBase):
    """
    Schema for creating a new product.

    Inherits all fields from ProductBase.
    """
    pass


class ProductUpdate(ProductBase):
    """
    Schema for updating an existing product.

    All fields are optional to allow partial updates.

    :param name: Updated product name.
    :type name: str | None

    :param description: Updated product description.
    :type description: str | None

    :param price: Updated product price.
    :type price: float | None

    :param stock: Updated product stock.
    :type stock: int | None
    """

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None


class ProductOut(ProductBase):
    """
    Schema for returning product information via API responses.

    :param id: Primary key of the product.
    :type id: int

    :param created_at: Timestamp (UTC) when the product was created.
    :type created_at: datetime | None

    :param updated_at: Timestamp (UTC) of the last update.
    :type updated_at: datetime | None
    """

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

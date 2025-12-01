# app/models/products.py

"""
Database model for storing product information.

This table is used to manage items available in the system's catalog.
It supports:
- Listing products
- Managing stock levels
- Handling pricing
- Tracking creation and update timestamps

Each entry represents a single product.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime, timezone

from app.database import Base


class Product(Base):
    """
    Represents a product available in the system.

    :param id: Primary key of the product.
    :type id: int

    :param name: Name of the product.
    :type name: str

    :param description: Detailed description of the product.
    :type description: str

    :param price: Monetary price of the product.
    :type price: float

    :param stock: Quantity of the product currently in stock.
    :type stock: int

    :param created_at: Timestamp (UTC) indicating when the product was created.
    :type created_at: datetime

    :param updated_at: Timestamp (UTC) indicating the last update to the product.
    :type updated_at: datetime
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False,  default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

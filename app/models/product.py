import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, Integer, String

from app.database import Base


class ProductType(str, enum.Enum):
    PLAT = "PLAT"
    DESSERT = "DESSERT"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(120), nullable=False)
    description = Column(String(500), nullable=True)
    type = Column(Enum(ProductType), nullable=False)
    prix = Column(Float, nullable=False)
    date_creation = Column(DateTime, default=datetime.utcnow, nullable=False)
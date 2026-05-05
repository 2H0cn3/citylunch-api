from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.product import ProductType


class ProductBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=500)
    type: ProductType
    prix: float = Field(..., gt=0, description="Prix TTC en euros, strictement positif")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=500)
    type: Optional[ProductType] = None
    prix: Optional[float] = Field(None, gt=0)


class ProductRead(ProductBase):
    id: int
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True)
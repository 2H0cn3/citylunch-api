from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.product import ProductRead


class SacItemRead(BaseModel):
    product: ProductRead
    quantite: int

    model_config = ConfigDict(from_attributes=True)


class SacContentResponse(BaseModel):
    livreur_id: int
    items: List[SacItemRead]


class SacAddRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantite: int = Field(..., gt=0, description="Quantité à ajouter (> 0)")


class SacRemoveRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantite: int = Field(..., gt=0, description="Quantité à retirer (> 0)")
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import sac as crud
from app.crud.sac import StockError
from app.database import get_db
from app.dependencies import get_current_livreur
from app.models.livreur import Livreur
from app.schemas.sac import (
    SacAddRequest,
    SacContentResponse,
    SacItemRead,
    SacRemoveRequest,
)

router = APIRouter(prefix="/sac", tags=["Sac (Livreur connecté)"])


@router.get("", response_model=SacContentResponse)
def get_my_sac(
    db: Session = Depends(get_db),
    current_livreur: Livreur = Depends(get_current_livreur),
):
    """Consulte le contenu courant du sac du livreur connecté."""
    sac = crud.get_sac_for_livreur(db, current_livreur.id)
    items = crud.list_items(db, sac)
    return SacContentResponse(
        livreur_id=current_livreur.id,
        items=[
            SacItemRead.model_validate(i, from_attributes=True) for i in items
        ],
    )


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    response_model=SacItemRead,
)
def add_to_sac(
    payload: SacAddRequest,
    db: Session = Depends(get_db),
    current_livreur: Livreur = Depends(get_current_livreur),
):
    """Ajoute un produit (en quantité) dans le sac du livreur connecté."""
    sac = crud.get_sac_for_livreur(db, current_livreur.id)
    try:
        item = crud.add_product(
            db, sac, payload.product_id, payload.quantite
        )
    except StockError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return SacItemRead.model_validate(item, from_attributes=True)


@router.delete("/items", response_model=SacItemRead)
def remove_from_sac(
    payload: SacRemoveRequest,
    db: Session = Depends(get_db),
    current_livreur: Livreur = Depends(get_current_livreur),
):
    """Retire un produit (en quantité) du sac du livreur connecté."""
    sac = crud.get_sac_for_livreur(db, current_livreur.id)
    try:
        item = crud.remove_product(
            db, sac, payload.product_id, payload.quantite
        )
    except StockError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return SacItemRead.model_validate(item, from_attributes=True)
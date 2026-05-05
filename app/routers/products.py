from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import product as crud
from app.database import get_db
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductRead])
def list_products(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.list_all(db, skip=skip, limit=limit)


@router.post(
    "", response_model=ProductRead, status_code=status.HTTP_201_CREATED
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    return crud.create(db, payload)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit introuvable.")
    return product


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)
):
    product = crud.get(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit introuvable.")
    return crud.update(db, product, payload)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit introuvable.")
    crud.delete(db, product)
    return None
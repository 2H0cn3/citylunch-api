from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.notifications import notify_new_livreur
from app.crud import livreur as crud
from app.database import get_db
from app.schemas.livreur import (
    LivreurCreate,
    LivreurCreatedResponse,
    LivreurRead,
    LivreurUpdate,
)

router = APIRouter(prefix="/livreurs", tags=["Livreurs"])


@router.get("", response_model=List[LivreurRead])
def list_livreurs(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.list_all(db, skip=skip, limit=limit)


@router.post(
    "",
    response_model=LivreurCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_livreur(payload: LivreurCreate, db: Session = Depends(get_db)):
    if crud.get_by_email(db, payload.email):
        raise HTTPException(
            status_code=409,
            detail="Un livreur avec cet email existe déjà.",
        )

    livreur, plain_password = crud.create(db, payload)
    notify_new_livreur(livreur.email, livreur.prenom, plain_password)

    return LivreurCreatedResponse(
        id=livreur.id,
        email=livreur.email,
        nom=livreur.nom,
        prenom=livreur.prenom,
        is_available=livreur.is_available,
        date_creation=livreur.date_creation,
        mot_de_passe_initial=plain_password,
    )


@router.get("/{livreur_id}", response_model=LivreurRead)
def get_livreur(livreur_id: int, db: Session = Depends(get_db)):
    livreur = crud.get(db, livreur_id)
    if livreur is None:
        raise HTTPException(status_code=404, detail="Livreur introuvable.")
    return livreur


@router.put("/{livreur_id}", response_model=LivreurRead)
def update_livreur(
    livreur_id: int, payload: LivreurUpdate, db: Session = Depends(get_db)
):
    livreur = crud.get(db, livreur_id)
    if livreur is None:
        raise HTTPException(status_code=404, detail="Livreur introuvable.")
    return crud.update(db, livreur, payload)


@router.delete("/{livreur_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_livreur(livreur_id: int, db: Session = Depends(get_db)):
    livreur = crud.get(db, livreur_id)
    if livreur is None:
        raise HTTPException(status_code=404, detail="Livreur introuvable.")
    crud.delete(db, livreur)
    return None
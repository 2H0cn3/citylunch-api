from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.crud import livreur as livreur_crud
from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    livreur = livreur_crud.get_by_email(db, payload.email)
    if livreur is None or not verify_password(
        payload.password, livreur.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides.",
        )

    token = create_access_token(subject=str(livreur.id))
    return TokenResponse(access_token=token)
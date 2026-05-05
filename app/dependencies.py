from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.livreur import Livreur

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_livreur(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Livreur:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception

    try:
        livreur_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise credentials_exception

    livreur = db.query(Livreur).filter(Livreur.id == livreur_id).first()
    if livreur is None:
        raise credentials_exception

    return livreur
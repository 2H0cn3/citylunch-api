from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.security import generate_random_password, hash_password
from app.models.livreur import Livreur
from app.models.sac import Sac
from app.schemas.livreur import LivreurCreate, LivreurUpdate


def get(db: Session, livreur_id: int) -> Optional[Livreur]:
    return db.query(Livreur).filter(Livreur.id == livreur_id).first()


def get_by_email(db: Session, email: str) -> Optional[Livreur]:
    return db.query(Livreur).filter(Livreur.email == email).first()


def list_all(db: Session, skip: int = 0, limit: int = 100) -> List[Livreur]:
    return db.query(Livreur).offset(skip).limit(limit).all()


def create(db: Session, data: LivreurCreate) -> Tuple[Livreur, str]:
    """Crée un livreur ET son sac.

    - Génère un mot de passe aléatoire sécurisé
    - Stocke uniquement son hash en base
    - Crée le sac associé
    - Retourne (livreur, mot_de_passe_en_clair) pour notification
    """
    plain_password = generate_random_password(12)

    livreur = Livreur(
        email=data.email,
        nom=data.nom,
        prenom=data.prenom,
        hashed_password=hash_password(plain_password),
        is_available=True,
    )
    db.add(livreur)
    db.flush()  # nécessaire pour récupérer l'id avant le commit

    sac = Sac(livreur_id=livreur.id)
    db.add(sac)

    db.commit()
    db.refresh(livreur)
    return livreur, plain_password


def update(db: Session, livreur: Livreur, data: LivreurUpdate) -> Livreur:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(livreur, field, value)
    db.commit()
    db.refresh(livreur)
    return livreur


def delete(db: Session, livreur: Livreur) -> None:
    db.delete(livreur)
    db.commit()
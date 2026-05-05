from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LivreurBase(BaseModel):
    email: EmailStr
    nom: str = Field(..., min_length=1, max_length=80)
    prenom: str = Field(..., min_length=1, max_length=80)


class LivreurCreate(LivreurBase):
    """Pas de mot de passe : il est généré automatiquement par l'API."""
    pass


class LivreurUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nom: Optional[str] = Field(None, min_length=1, max_length=80)
    prenom: Optional[str] = Field(None, min_length=1, max_length=80)
    is_available: Optional[bool] = None


class LivreurRead(LivreurBase):
    id: int
    is_available: bool
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True)


class LivreurCreatedResponse(LivreurRead):
    """Réponse retournée à la création.

    Le mot de passe initial est exposé une seule fois ici, en complément
    de la notification envoyée au livreur. Pratique pour les tests Postman
    et pour permettre au gérant de le retransmettre si besoin.
    """

    mot_de_passe_initial: str
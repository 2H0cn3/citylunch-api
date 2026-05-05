from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Livreur(Base):
    __tablename__ = "livreurs"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    nom = Column(String(80), nullable=False)
    prenom = Column(String(80), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    date_creation = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relation 1-1 vers le sac (créé en même temps que le livreur)
    sac = relationship(
        "Sac",
        back_populates="livreur",
        uselist=False,
        cascade="all, delete-orphan",
    )
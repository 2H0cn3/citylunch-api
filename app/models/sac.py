import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class MovementType(str, enum.Enum):
    AJOUT = "AJOUT"      # chargement / réapprovisionnement
    RETRAIT = "RETRAIT"  # livraison ou rendu en fin de service


class Sac(Base):
    __tablename__ = "sacs"

    id = Column(Integer, primary_key=True, index=True)
    livreur_id = Column(
        Integer, ForeignKey("livreurs.id"), unique=True, nullable=False
    )
    date_creation = Column(DateTime, default=datetime.utcnow, nullable=False)

    livreur = relationship("Livreur", back_populates="sac")
    items = relationship(
        "SacItem", back_populates="sac", cascade="all, delete-orphan"
    )
    mouvements = relationship(
        "MouvementStock", back_populates="sac", cascade="all, delete-orphan"
    )


class SacItem(Base):
    """Contenu courant du sac (vue agrégée par produit)."""

    __tablename__ = "sac_items"
    __table_args__ = (
        UniqueConstraint("sac_id", "product_id", name="uq_sac_product"),
    )

    id = Column(Integer, primary_key=True, index=True)
    sac_id = Column(Integer, ForeignKey("sacs.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantite = Column(Integer, nullable=False, default=0)

    sac = relationship("Sac", back_populates="items")
    product = relationship("Product")


class MouvementStock(Base):
    """Historique de tous les mouvements de stock du sac."""

    __tablename__ = "mouvements_stock"

    id = Column(Integer, primary_key=True, index=True)
    sac_id = Column(Integer, ForeignKey("sacs.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantite = Column(Integer, nullable=False)
    type = Column(Enum(MovementType), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)

    sac = relationship("Sac", back_populates="mouvements")
    product = relationship("Product")
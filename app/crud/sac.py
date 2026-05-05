from typing import List

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sac import MouvementStock, MovementType, Sac, SacItem


class StockError(Exception):
    """Erreur métier liée aux opérations de stock du sac."""


def get_sac_for_livreur(db: Session, livreur_id: int) -> Sac:
    """Récupère le sac du livreur. Le crée s'il n'existe pas (filet de sécurité)."""
    sac = db.query(Sac).filter(Sac.livreur_id == livreur_id).first()
    if sac is None:
        sac = Sac(livreur_id=livreur_id)
        db.add(sac)
        db.commit()
        db.refresh(sac)
    return sac


def list_items(db: Session, sac: Sac) -> List[SacItem]:
    """Retourne uniquement les items réellement présents (quantité > 0)."""
    return [item for item in sac.items if item.quantite > 0]


def add_product(
    db: Session, sac: Sac, product_id: int, quantite: int
) -> SacItem:
    """Ajoute `quantite` unités du produit au sac et journalise le mouvement."""
    if quantite <= 0:
        raise StockError("La quantité doit être strictement positive.")

    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise StockError(f"Le produit {product_id} n'existe pas.")

    item = (
        db.query(SacItem)
        .filter(SacItem.sac_id == sac.id, SacItem.product_id == product_id)
        .first()
    )
    if item is None:
        item = SacItem(sac_id=sac.id, product_id=product_id, quantite=quantite)
        db.add(item)
    else:
        item.quantite += quantite

    db.add(
        MouvementStock(
            sac_id=sac.id,
            product_id=product_id,
            quantite=quantite,
            type=MovementType.AJOUT,
        )
    )

    db.commit()
    db.refresh(item)
    return item


def remove_product(
    db: Session, sac: Sac, product_id: int, quantite: int
) -> SacItem:
    """Retire `quantite` unités du sac.

    Règle métier : on ne peut pas retirer plus que ce qui est présent
    (le stock du sac ne peut pas devenir négatif).
    """
    if quantite <= 0:
        raise StockError("La quantité doit être strictement positive.")

    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise StockError(f"Le produit {product_id} n'existe pas.")

    item = (
        db.query(SacItem)
        .filter(SacItem.sac_id == sac.id, SacItem.product_id == product_id)
        .first()
    )

    en_stock = item.quantite if item else 0
    if en_stock < quantite:
        raise StockError(
            f"Stock insuffisant : {en_stock} unité(s) en sac, "
            f"retrait de {quantite} demandé."
        )

    item.quantite -= quantite

    db.add(
        MouvementStock(
            sac_id=sac.id,
            product_id=product_id,
            quantite=quantite,
            type=MovementType.RETRAIT,
        )
    )

    db.commit()
    db.refresh(item)
    return item
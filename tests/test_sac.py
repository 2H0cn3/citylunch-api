"""Test unitaire d'une règle métier de CityLunch.

Règle métier testée :
    Un livreur ne peut PAS retirer de son sac plus d'unités d'un produit
    qu'il n'en contient. Le stock du sac ne peut jamais devenir négatif.
    En cas de violation, aucune modification (ni du stock, ni de l'historique
    des mouvements) ne doit être enregistrée.

Cette règle reflète l'exigence du sujet : « Tous les mouvements de stock sont
enregistrés » (cohérence) et garantit l'intégrité du suivi des sacs.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.crud import sac as sac_crud
from app.crud.sac import StockError
from app.database import Base
from app.models.livreur import Livreur
from app.models.product import Product, ProductType
from app.models.sac import MouvementStock, MovementType, Sac


@pytest.fixture
def db_session():
    """Session SQLAlchemy isolée sur SQLite en mémoire."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def setup_data(db_session):
    """Crée un livreur, son sac et un plat de référence."""
    livreur = Livreur(
        email="jean.dupont@citylunch.fr",
        nom="Dupont",
        prenom="Jean",
        hashed_password=hash_password("dummy-password-1234"),
    )
    db_session.add(livreur)
    db_session.flush()

    sac = Sac(livreur_id=livreur.id)
    db_session.add(sac)

    plat = Product(nom="Poulet rôti", type=ProductType.PLAT, prix=12.5)
    db_session.add(plat)

    db_session.commit()
    db_session.refresh(livreur)
    db_session.refresh(sac)
    db_session.refresh(plat)

    return {"livreur": livreur, "sac": sac, "plat": plat}


def test_ajout_puis_retrait_partiel_decremente_correctement(
    db_session, setup_data
):
    """Cas nominal : retirer moins que le stock fonctionne."""
    sac = setup_data["sac"]
    plat = setup_data["plat"]

    sac_crud.add_product(db_session, sac, plat.id, 5)
    sac_crud.remove_product(db_session, sac, plat.id, 2)

    items = sac_crud.list_items(db_session, sac)
    assert len(items) == 1
    assert items[0].quantite == 3


def test_retirer_plus_que_le_stock_disponible_leve_une_erreur(
    db_session, setup_data
):
    """Cas critique : on ne peut pas retirer plus que le stock présent.

    Vérifie également qu'aucune modification parasite n'est persistée :
        - le stock reste inchangé,
        - aucun mouvement de RETRAIT n'est enregistré.
    """
    sac = setup_data["sac"]
    plat = setup_data["plat"]

    # On charge 3 plats dans le sac
    sac_crud.add_product(db_session, sac, plat.id, 3)

    # Tenter d'en retirer 5 doit lever une StockError
    with pytest.raises(StockError) as exc_info:
        sac_crud.remove_product(db_session, sac, plat.id, 5)

    assert "insuffisant" in str(exc_info.value).lower()

    # Le stock doit être inchangé après l'échec
    items = sac_crud.list_items(db_session, sac)
    assert len(items) == 1
    assert items[0].quantite == 3

    # Aucun mouvement de RETRAIT n'a été journalisé
    nb_retraits = (
        db_session.query(MouvementStock)
        .filter(
            MouvementStock.sac_id == sac.id,
            MouvementStock.type == MovementType.RETRAIT,
        )
        .count()
    )
    assert nb_retraits == 0

    # En revanche, l'AJOUT initial est bien tracé
    nb_ajouts = (
        db_session.query(MouvementStock)
        .filter(
            MouvementStock.sac_id == sac.id,
            MouvementStock.type == MovementType.AJOUT,
        )
        .count()
    )
    assert nb_ajouts == 1
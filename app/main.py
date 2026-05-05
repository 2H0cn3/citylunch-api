from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import auth, livreurs, products, sac

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API REST sécurisée et documentée pour CityLunch.\n\n"
        "- Partie 1 : CRUD Produits & Livreurs (public)\n"
        "- Partie 2 : Authentification JWT, gestion du sac d'un livreur\n"
    ),
    version="1.0.0",
)

app.include_router(products.router)
app.include_router(livreurs.router)
app.include_router(auth.router)
app.include_router(sac.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "status": "ok",
        "docs": "/docs",
        "redoc": "/redoc",
    }
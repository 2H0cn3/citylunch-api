# CityLunch API

API REST sécurisée et documentée pour CityLunch : gestion des produits, des livreurs et de leur sac de livraison. Authentification par JWT, mots de passe hashés en bcrypt, journalisation complète des mouvements de stock.

Réalisée en **Python / FastAPI** dans le cadre de l'épreuve **EC03 Back — Développement d'une API sécurisée et documentée**.

> 🔗 **Dépôt Git public :** https://github.com/<TON_USER>/citylunch-api

---

## Composants nécessaires au fonctionnement du projet

### Prérequis système
- **Python 3.11 ou supérieur**
- **pip** (livré avec Python)
- **git**

### Dépendances Python (installées via `requirements.txt`)

| Composant         | Rôle                                                  |
|-------------------|-------------------------------------------------------|
| FastAPI           | Framework web et génération automatique d'OpenAPI     |
| Uvicorn           | Serveur ASGI pour lancer l'API                        |
| SQLAlchemy 2      | ORM (mapping objet-relationnel)                       |
| SQLite            | Base de données embarquée (fichier `citylunch.db`)    |
| Pydantic v2       | Validation des entrées et sérialisation des sorties   |
| python-jose       | Signature et vérification des tokens JWT              |
| passlib + bcrypt  | Hashage sécurisé des mots de passe livreurs           |
| pytest            | Framework de tests unitaires                          |
| httpx             | Client HTTP utilisé par les tests                     |

> La base SQLite est créée automatiquement à la racine du projet au premier lancement de l'API. Aucun serveur de base de données à installer.

---

## Initialisation du projet

Pour un développeur reprenant le projet à partir du dépôt Git :

```bash
# 1. Cloner le dépôt
git clone https://github.com/<TON_USER>/citylunch-api.git
cd citylunch-api

# 2. Créer un environnement virtuel et l'activer
python3 -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows (PowerShell)
# source .venv/Scripts/activate    # Windows (Git Bash)

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. (Recommandé) Définir un secret JWT robuste dans un fichier .env
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))" > .env

# 5. Lancer l'API en mode développement
uvicorn app.main:app --reload
```

Une fois lancée, l'API est accessible sur :

- **API** : http://localhost:8000
- **Documentation interactive (Swagger UI)** : http://localhost:8000/docs
- **Documentation alternative (ReDoc)** : http://localhost:8000/redoc

---

## Commande pour exécuter les tests

```bash
pytest tests/ -v
```

Sortie attendue :

```
tests/test_sac.py::test_ajout_puis_retrait_partiel_decremente_correctement PASSED
tests/test_sac.py::test_retirer_plus_que_le_stock_disponible_leve_une_erreur PASSED
======================== 2 passed ========================
```

Le test unitaire valide la règle métier suivante :
> Un livreur ne peut pas retirer de son sac plus d'unités d'un produit qu'il n'en contient. En cas de violation, ni le stock ni l'historique des mouvements ne doivent être modifiés.

---

## Adresse du dépôt Git (public)

**https://github.com/<TON_USER>/citylunch-api**

L'historique est organisé en branches de feature, une par partie du sujet :
- `main` — branche principale, intègre toutes les parties
- `feature/part-1-crud` — CRUD public produits & livreurs
- `feature/part-2-auth-and-bag` — authentification JWT et gestion du sac
- `feature/part-3-tests` — test unitaire de la règle métier

Visualiser : `git log --all --graph --oneline --decorate`

---

## Endpoints

| Méthode | Route                | Auth | Description                                |
|--------:|----------------------|:----:|--------------------------------------------|
| GET     | `/products`          |  ❌  | Lister les produits                        |
| POST    | `/products`          |  ❌  | Créer un produit (PLAT \| DESSERT)         |
| GET     | `/products/{id}`     |  ❌  | Consulter un produit                       |
| PUT     | `/products/{id}`     |  ❌  | Modifier un produit                        |
| DELETE  | `/products/{id}`     |  ❌  | Supprimer un produit                       |
| GET     | `/livreurs`          |  ❌  | Lister les livreurs                        |
| POST    | `/livreurs`          |  ❌  | Créer un livreur (génère mdp + sac + notif)|
| GET     | `/livreurs/{id}`     |  ❌  | Consulter un livreur                       |
| PUT     | `/livreurs/{id}`     |  ❌  | Modifier un livreur                        |
| DELETE  | `/livreurs/{id}`     |  ❌  | Supprimer un livreur                       |
| POST    | `/auth/login`        |  ❌  | Se connecter, recevoir un JWT              |
| GET     | `/sac`               |  ✅  | Consulter le contenu de son sac            |
| POST    | `/sac/items`         |  ✅  | Ajouter un produit dans son sac            |
| DELETE  | `/sac/items`         |  ✅  | Retirer un produit de son sac              |

Les routes marquées ✅ requièrent le header `Authorization: Bearer <jwt_token>` obtenu via `POST /auth/login`.

---

## Structure du projet

```
citylunch-api/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── config.py            # Configuration (env)
│   ├── database.py          # Engine + session SQLAlchemy
│   ├── dependencies.py      # Dépendance JWT (get_current_livreur)
│   ├── models/              # Tables ORM (Product, Livreur, Sac, MouvementStock)
│   ├── schemas/             # Validation Pydantic
│   ├── core/                # Sécurité (bcrypt, JWT) + notifications
│   ├── crud/                # Logique métier
│   └── routers/             # Endpoints REST
├── tests/
│   └── test_sac.py          # Test unitaire de la règle métier
├── docs/
│   ├── MCD.md               # Modèle Conceptuel de Données
│   └── citylunch.postman_collection.json
├── test-all.sh              # Smoke test bout-en-bout (14 endpoints)
├── git-replay.sh            # Reconstruction de l'historique Git par branches
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Livrables

| Livrable                                  | Emplacement                                  |
|-------------------------------------------|----------------------------------------------|
| Code source de l'application              | `app/`                                       |
| Test unitaire                             | `tests/test_sac.py`                          |
| Modèle Conceptuel de Données              | `docs/MCD.md`                                |
| Export des routes (Postman)               | `docs/citylunch.postman_collection.json`     |
| README                                    | `README.md`                                  |
| Dépôt Git public                          | https://github.com/2H0cn3/citylunch-api.git  |

---

## Notes complémentaires

- **Notification livreur** : à la création d'un livreur, son mot de passe initial est généré côté serveur, hashé en base, et imprimé dans la console serveur (stub à brancher sur un service email réel en production).
- **Codes HTTP** : 201 (création), 200 (succès), 204 (suppression), 400 (règle métier violée), 401 (non authentifié), 404 (introuvable), 409 (conflit), 422 (payload invalide).
- **Migrations** : `Base.metadata.create_all` est utilisé au démarrage. Pour la production, prévoir une migration avec Alembic.
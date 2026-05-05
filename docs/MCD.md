# Modèle Conceptuel de Données — CityLunch

## Diagramme entité-relation

```mermaid
erDiagram
    LIVREUR ||--|| SAC : possede
    SAC ||--o{ SAC_ITEM : contient
    SAC ||--o{ MOUVEMENT_STOCK : journalise
    PRODUIT ||--o{ SAC_ITEM : reference
    PRODUIT ||--o{ MOUVEMENT_STOCK : concerne

    LIVREUR {
        int id PK
        string email UK
        string nom
        string prenom
        string hashed_password
        bool is_available
        datetime date_creation
    }

    PRODUIT {
        int id PK
        string nom
        string description
        enum type "PLAT|DESSERT"
        float prix
        datetime date_creation
    }

    SAC {
        int id PK
        int livreur_id FK,UK
        datetime date_creation
    }

    SAC_ITEM {
        int id PK
        int sac_id FK
        int product_id FK
        int quantite
    }

    MOUVEMENT_STOCK {
        int id PK
        int sac_id FK
        int product_id FK
        int quantite
        enum type "AJOUT|RETRAIT"
        datetime date
    }
```

## Cardinalités

| Relation                       | Cardinalité | Contrainte                                 |
|--------------------------------|:-----------:|--------------------------------------------|
| Livreur — Sac                  | 1 — 1       | unicité de `sac.livreur_id`                |
| Sac — SacItem                  | 1 — 0..n    | UNIQUE (sac, produit) sur SacItem          |
| Sac — MouvementStock           | 1 — 0..n    | append-only (audit)                        |
| Produit — SacItem              | 1 — 0..n    |                                            |
| Produit — MouvementStock       | 1 — 0..n    |                                            |
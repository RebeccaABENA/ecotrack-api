<img width="956" height="478" alt="image" src="https://github.com/user-attachments/assets/3eda7fe7-3689-4b2e-ac96-b9a203dc04ab" />


Projet EcoTrack : une API FastAPI pour explorer et gérer des indicateurs environnementaux (qualité de l’air, mesures par zone), avec un front HTML/CSS/JS intégré.

Le projet a été réalisé dans le cadre d’un TP d’API avec les objectifs suivants :

- Exposer une API REST propre (CRUD, filtres, validation).
- Utiliser une base SQLite avec SQLAlchemy + Alembic.
- Intégrer un système d’authentification par JWT (utilisateurs + rôles).
- Importer des données réelles depuis des fichiers CSV.
- Proposer un front minimaliste pour consommer et tester l’API.

<img width="959" height="480" alt="image" src="https://github.com/user-attachments/assets/9b60b8ec-cfb4-465a-a46f-820460182fe6" />

<img width="960" height="477" alt="image" src="https://github.com/user-attachments/assets/7f07d494-dfd9-4038-ad1c-23228b130292" />

## 1. Stack technique

- **Langage** : Python 
- **Framework API** : FastAPI
- **ORM** : SQLAlchemy
- **Migrations** : Alembic
- **Auth** : JWT (via `python-jose`), hashing des mots de passe (`passlib[bcrypt]`)
- **Base de données** : SQLite
- **Front** : `index.html` (HTML / CSS / JS vanilla) + Chart.js pour les graphes

---

<img width="960" height="457" alt="image" src="https://github.com/user-attachments/assets/d7870b7e-124a-46f7-83e2-fe5d623f5b39" />

## 2. Architecture du projet

Organisation des fichiers :

```text
ecotrack-api/
  app/
    __init__.py
    main.py               # Point d’entrée FastAPI (sert aussi le front index.html)
    index.html            # Front-end HTML/CSS/JS
    auth.py               # Routes /register, /login, /me + gestion JWT
    indicators_routes.py  # Routes liées aux indicateurs /api/indicators...
    importer.py           # Fonctions d’import depuis les fichiers CSV
    models.py             # Modèles SQLAlchemy (User, Indicator, Zone, Source, ...)
    database.py           # Engine, SessionLocal, dépendance get_db
    crud.py               # Logique métier (CRUD sur Indicator, User.)
    schemas.py            # Schémas Pydantic (User*, Indicator*)
  data/
    ind_atmo_2021.csv     # Jeu de données 1 (qualité de l’air / indice Atmo)
    FR_E2_2025-01-01.csv  # Jeu de données 2 (mesures complémentaires)
  alembic/
    env.py
    versions/             # Scripts de migrations
  init.py                 # Script pour remplir la BDD à partir des CSV
  requirements.txt
  alembic.ini

  README.md


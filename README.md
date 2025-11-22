# Projet EcoTrack :

est une applicatiion web qui permet d' explorer et gérer des indicateurs environnementaux (qualité de l’air, mesures par zone), avec un front HTML/CSS/JS intégré.

<img width="956" height="478" alt="image" src="https://github.com/user-attachments/assets/3eda7fe7-3689-4b2e-ac96-b9a203dc04ab" />


Le projet a été réalisé dans le cadre d’un TP d’API avec les objectifs suivants :

- Exposer une API REST propre (CRUD, filtres, validation).
- Utiliser une base SQLite avec SQLAlchemy + Alembic.
- Intégrer un système d’authentification par JWT (utilisateurs + rôles).
- Importer des données réelles depuis des fichiers CSV.
- Proposer un front minimaliste pour consommer et tester l’API.

<img width="960" height="479" alt="image" src="https://github.com/user-attachments/assets/5941b525-ce84-4d98-9d88-459550bb51d2" />


<img width="566" height="265" alt="image" src="https://github.com/user-attachments/assets/f399b78b-bbf2-4b8e-a53b-ec009e908ce1" />


<img width="960" height="477" alt="image" src="https://github.com/user-attachments/assets/7f07d494-dfd9-4038-ad1c-23228b130292" />

## Stack technique
- **Langage** : Python 
- **Framework API** : FastAPI
- **ORM** : SQLAlchemy
- **Migrations** : Alembic
- **Auth** : JWT (via `python-jose`), hashing des mots de passe (`passlib[bcrypt]`)
- **Base de données** : SQLite
- **Front** : `index.html` (HTML / CSS / JS vanilla) + Chart.js pour les graphes

##  Architecture du projet

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

```

## Fonctionnalités clés

L’application EcoTrack permet de :

Charger des données environnementales depuis des fichiers CSV (qualité de l’air, indicateurs par zone) et les stocker dans une base SQLite.

Exposer une API REST pour consulter ces indicateurs (liste, filtres, pagination).

Sécuriser l’accès via un système d’authentification JWT :

rôle user : consultation et visualisation des données,

rôle admin : gestion complète des indicateurs (création, modification, suppression).

Offrir un front-end web (HTML/CSS/JS) pour :

se connecter / s’inscrire,

explorer les données sous forme de tableau filtrable,

afficher des graphiques d’évolution dans le temps,

administrer les indicateurs (interface admin).

En résumé : les CSV alimentent la base ; l’API expose les données ; le front consomme l’API.

## Rôle des principaux fichiers
Fichiers back-end (app/)

### app/main.py
Point d’entrée de l’application :

crée l’instance FastAPI,

monte les routeurs (authentification, indicateurs),

sert le front (GET / renvoie index.html).

### app/database.py
Gestion de la base de données :

configure l’engine SQLite,

définit SessionLocal (sessions SQLAlchemy),

fournit la dépendance get_db() utilisée dans les endpoints pour accéder à la base.

### app/models.py
Modèles SQLAlchemy (ORM) :

User : représente un utilisateur (id, email, password_hash, role),

Indicator : représente un indicateur environnemental (source, zone, type, valeur, date, etc.).

### app/schemas.py
Schémas Pydantic :

structures des données en entrée/sortie des endpoints,

validation des payloads (types, champs obligatoires),

ex. : UserCreate, UserRead, IndicatorCreate, IndicatorUpdate, IndicatorRead.

### app/auth.py
Gestion de l’authentification :

POST /register : inscription d’un utilisateur (hash du mot de passe, rôle),

POST /login : génération d’un token JWT si les identifiants sont corrects,

GET /me : renvoie les infos de l’utilisateur connecté,

fonctions utilitaires pour décoder le token et récupérer l’utilisateur courant.

### app/crud.py
Logique métier / accès aux données :

fonctions pour créer, lire, mettre à jour et supprimer des indicateurs,

encapsule les requêtes SQLAlchemy pour garder les routes plus simples.

### app/indicators_routes.py
Routes liées aux indicateurs :

GET /api/indicators : liste + filtres (type, zone, source, période, pagination),

POST /api/indicators : création (réservé aux admins),

PUT /api/indicators/{id} : mise à jour (admin),

DELETE /api/indicators/{id} : suppression (admin),

utilise get_current_user pour vérifier le rôle.

### app/importer.py
Import des fichiers CSV :

lit ligne par ligne les fichiers (par ex. ind_atmo_2021.csv, FR_E2_2025-01-01.csv),

nettoie / convertit les données (dates, nombres),

crée des objets Indicator et les insère en base,

retourne un résumé (lignes insérées, erreurs).

### Script d’initialisation

init.py (à la racine du projet)
Script pour remplir la base de données avec les CSV :

ouvre une session sur la BDD,

appelle les fonctions d’importer.py pour chaque fichier CSV,

affiche dans la console le nombre de lignes insérées et les éventuelles erreurs.

Front-end

### app/index.html
Interface web en HTML/CSS/JS :

formulaire d’inscription et de connexion,

gestion du token JWT côté navigateur,

appels fetch vers l’API pour :

récupérer et filtrer les indicateurs,

afficher un tableau de résultats,

afficher des graphiques d’évolution,

gérer les formulaires de création / modification / suppression côté admin,

affichage des messages d’erreur renvoyés par l’API.


## ⚙️ Guide d'Installation

Suivez ces étapes pour lancer le projet sur votre machine locale.

### Prérequis
* **Python** 
* **Git** 

### Étape 1 : Récupérer le projet
Ouvrez votre terminal et lancez :
```bash
git clone git@github.com:RebeccaABENA/ecotrack-api.git
cd ecotrack
```
### Étape 2 : Préparer l'environnement virtuel
Il est recommandé d'isoler les bibliothèques du projet.

Sous Windows :

```bash

python -m venv vecotrack
venv\Scripts\activate
```
Sous Mac / Linux :

```Bash

python3 -m venv vecotrack
source venv/bin/activate
```
Étape 3 : Installer les dépendances
Installez les librairies nécessaires (FastAPI, SQLAlchemy, etc.) :

```Bash

pip install -r requirements.txt
```

Étape 4 : Lancer le Serveur (Backend)
Assurez-vous d'être dans le dossier contenant le dossier app et lancez :

```Bash

uvicorn app.main:app --reload
```
### Le terminal doit afficher : Application startup complete.

Étape 5 : Lancer l'Application (Frontend)
Ouvrez le dossier app dans votre explorateur de fichiers.
Double-cliquez sur le fichier index.html.

## Votre navigateur s'ouvre : l'application est prête à etre utilisée !

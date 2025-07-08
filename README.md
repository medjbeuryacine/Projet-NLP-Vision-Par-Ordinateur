# Projet NLP & Vision Par Ordinateur

Une application web full-stack pour l'analyse et la prédiction de modèles d'intelligence artificielle combinant traitement du langage naturel (NLP) et vision par ordinateur.

## Architecture du Projet 

### Backend (FastAPI)
- **Framework** : FastAPI avec Python
- **Base de données** : MongoDB
- **Authentification** : JWT avec bcrypt
- **Modèles IA** : PyTorch pour les modèles de vision et NLP
- **Fonctionnalités** :
  - Gestion des utilisateurs et authentification
  - Chargement et analyse de modèles IA
  - API REST pour les prédictions
  - Traduction multilingue
  - Système d'emojis contextuels

### Frontend (React + Vite)
- **Framework** : React 18 avec Vite
- **Routing** : React Router
- **État global** : Context API
- **Interface** : Composants modulaires
- **Fonctionnalités** :
  - Interface d'authentification
  - Upload et analyse de modèles
  - Affichage des résultats en temps réel
  - Dashboard utilisateur

### Base de Données
- **MongoDB** avec deux collections principales :
  - `utilisateurs` : Gestion des comptes utilisateurs
  - `Models_IA` : Stockage des métadonnées des modèles

## Installation et Lancement

### Prérequis
- Docker et Docker Compose
- Git LFS (pour les fichiers modèles lourds)

### 1. Cloner le repository
```bash
git clone https://github.com/medjbeuryacine/Projet-NLP-Vision-Par-Ordinateur.git
cd Projet-NLP-Vision-Par-Ordinateur
```

### 2. Lancer l'application
```bash
docker-compose up --build -d
```

### 3. Accès aux services
- **Application Frontend** : http://localhost:3000
- **API Backend** : http://localhost:8000
- **Interface MongoDB** : http://localhost:8081
- **Documentation API** : http://localhost:8000/docs

## Configuration de la Base de Données

### 1. Créer la base de données
Accédez à l'interface MongoDB sur http://localhost:8081 et créez :

- **Nom de la base** : `Projet_NLP_&_CV`
- **Collections** :
  - `utilisateurs`
  - `Models_IA`

### 2. Créer un utilisateur
Utilisez la route POST `/users/create` pour créer votre premier utilisateur :

```json
{
  "nom": "string",
  "prenom": "string",
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

**Exemple avec curl** :
```bash
curl -X POST "http://localhost:8000/users/create" \
  -H "Content-Type: application/json" \
  -d '{
  "nom": "admin",
  "prenom": "admin",
  "username": "admin",
  "email": "admin@example.com",
  "password": "admin"
}'
```

### 3. Connexion
Utilisez la route POST `/users/login` pour vous connecter :

```json
{
  "email": "votre_email@example.com",
  "password": "votre_mot_de_passe"
}
```

## Structure des Modèles

Le projet utilise des modèles PyTorch pré-entraînés stockés dans `backend/models_stable_v2/` :
- `best_model_v2.pth` : Modèle principal pour les prédictions
- `model_loader.py` : Chargeur de modèles avec optimisations

## Fonctionnalités Principales

### Analyse de Modèles IA
- Upload de fichiers modèles
- Analyse automatique des architectures
- Prédictions en temps réel
- Visualisation des résultats

### Gestion Utilisateurs
- Inscription et authentification sécurisée
- Sessions JWT
- Profils utilisateurs personnalisés

### Traitement Multilingue
- Support de plusieurs langues
- Traduction automatique des résultats
- Détection automatique de la langue

### Interface Intuitive
- Design responsive
- Upload par drag & drop
- Résultats en temps réel
- Notifications contextuelles

## Technologies Utilisées

### Backend
- **FastAPI** : Framework web moderne et performant
- **PyTorch** : Framework de deep learning
- **MongoDB** : Base de données NoSQL
- **JWT** : Authentification sécurisée
- **Pydantic** : Validation des données

### Frontend
- **React** : Bibliothèque UI
- **Vite** : Build tool rapide
- **React Router** : Routing côté client
- **Context API** : Gestion d'état

### DevOps
- **Docker** : Conteneurisation
- **Docker Compose** : Orchestration multi-services
- **Git LFS** : Gestion des fichiers volumineux

## Ports et Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Interface utilisateur React |
| Backend | 8000 | API FastAPI |
| MongoDB | 27017 | Base de données |
| Mongo Express | 8081 | Interface d'administration MongoDB |

## Développement

### Structure du Code
```
├── backend/           # API FastAPI
│   ├── DataBase/     # Connexions BDD
│   ├── routes/       # Routes API
│   ├── models_stable_v2/  # Modèles IA
│   ├── security/     # Authentification
│   ├── shemas/       # Validation Pydantic
│   └── utils/        # Utilitaires
├── frontend/         # Application React
│   └── src/
│       ├── components/  # Composants React
│       ├── pages/      # Pages principales
│       ├── contexts/   # Context API
│       └── services/   # Services API
└── docker-compose.yaml
```

### API Endpoints Principaux
- `POST /users/create` : Inscription utilisateur
- `POST /users/login` : Connexion utilisateur
- `GET /model_info` : Récupération les information de model 
- `POST /generate_caption` : Prédictions en temps réel

## Sécurité

- Authentification JWT avec refresh tokens
- Hashage des mots de passe avec bcrypt
- Validation stricte des données d'entrée
- Protection CORS configurée
- Isolation des services via Docker
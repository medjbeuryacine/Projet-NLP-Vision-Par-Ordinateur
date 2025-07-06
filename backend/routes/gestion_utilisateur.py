from fastapi import APIRouter, HTTPException, status, Depends, Header
from shemas.gesstion_utilisateur_shemas import UserCreate, UserLogin, UserResponse, UserUpdate
from datetime import datetime
from bson import ObjectId
from DataBase.connecte_bdd_utilisateur import (
    users_collection, 
    hash_password, 
    verify_password, 
    user_exists,
    get_database_stats,
    db,
    user_exists_exclude_id
)
from security.auth import create_access_token, get_current_user
from jose import jwt


router = APIRouter(tags=["Gestion Utilisateurs MongoDB"])

def serialize_user(user_doc):
    """Convertit un document MongoDB en dictionnaire sérialisable"""
    if user_doc:
        user_doc["id"] = str(user_doc["_id"])
        del user_doc["_id"]
    return user_doc


@router.get("/database/stats")
async def database_stats(current_user: dict = Depends(get_current_user)):
    """Statistiques de la base de données"""
    return get_database_stats()

@router.post("/users/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, authorization: str = Header(None)):
    """Créer un nouvel utilisateur"""
    
    # Vérifier la connexion MongoDB
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de base de données non disponible"
        )
    
    try:
        user_count = users_collection.count_documents({})
        
        if user_count > 0:
            # Il y a déjà des utilisateurs, vérifier le token
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token requis pour créer un utilisateur"
                )
            
            # Vérifier le token
            token = authorization.split(" ")[1]
            try:
                payload = jwt.decode(token, "ma-super-cle-ultra-secrete-2024-mongo-api-xyz789", algorithms=["HS256"])
                user_id = payload.get("user_id")
                if not user_id:
                    raise HTTPException(401, "Token invalide")
            except:
                raise HTTPException(401, "Token invalide")
            

        # Vérifier si l'utilisateur existe déjà
        if user_exists(username=user.username, email=user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec ce nom d'utilisateur ou email existe déjà"
            )
        
        # Hacher le mot de passe
        hashed_password = hash_password(user.password)
        
        # Créer le document utilisateur
        user_doc = {
            "nom": user.nom,
            "prenom": user.prenom,
            "username": user.username,
            "password": hashed_password,
            "email": user.email,    
            "created_at": datetime.now(),
            "is_active": True
        }
        
        # Insérer l'utilisateur dans MongoDB
        result = users_collection.insert_one(user_doc)
        
        # Récupérer l'utilisateur créé
        created_user = users_collection.find_one({"_id": result.inserted_id})
        
        return UserResponse(
            id=str(created_user["_id"]),
            nom=created_user.get("nom"),
            prenom=created_user.get("prenom"),
            username=created_user["username"],
            email=created_user["email"],  
            created_at=created_user["created_at"],
            is_active=created_user["is_active"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de l'utilisateur: {str(e)}"
        )

@router.post("/users/login")
async def login_user(login_data: UserLogin):
    """Connexion utilisateur"""
    
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de base de données non disponible"
        )
    
    try:
        # Rechercher l'utilisateur
        user = users_collection.find_one({"email": login_data.email})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom d'utilisateur ou mot de passe incorrect"
            )
        
        # Vérifier le mot de passe
        if not verify_password(login_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom d'utilisateur ou mot de passe incorrect"
            )
        
        token = create_access_token(str(user["_id"]), user["email"])
        
        return {
            "message": "Connexion réussie",
            "access_token": token,
            "token_type": "bearer",
            "user_id": str(user["_id"]),
            "username": user["username"],
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la connexion: {str(e)}"
        )
    

@router.put("/users/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Modifier un utilisateur"""
    
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de base de données non disponible"
        )
    
    try:
        # Vérifier si l'utilisateur existe
        existing_user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Préparer les données de mise à jour
        update_data = {}
        
        # Vérifier l'unicité du username et email (si modifiés)
        if user_update.username and user_update.username != existing_user.get("username"):
            if user_exists_exclude_id(user_id, username=user_update.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ce nom d'utilisateur est déjà utilisé"
                )
            update_data["username"] = user_update.username
        
        if user_update.email and user_update.email != existing_user.get("email"):
            if user_exists_exclude_id(user_id, email=user_update.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cet email est déjà utilisé"
                )
            update_data["email"] = user_update.email
        
        # Ajouter les autres champs si fournis
        if user_update.nom is not None:
            update_data["nom"] = user_update.nom
        
        if user_update.prenom is not None:
            update_data["prenom"] = user_update.prenom
        
        if user_update.password:
            update_data["password"] = hash_password(user_update.password)
        
        # Ajouter la date de modification
        update_data["updated_at"] = datetime.utcnow()
        
        # Effectuer la mise à jour
        if update_data:
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
        
        # Récupérer l'utilisateur mis à jour
        updated_user = users_collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        
        return {
            "message": "Utilisateur mis à jour avec succès",
            "user": serialize_user(updated_user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )

@router.get("/users/list")
async def list_users(current_user: dict = Depends(get_current_user)):
    """Lister tous les utilisateurs (sans mots de passe)"""
    
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de base de données non disponible"
        )
    
    try:
        users = list(users_collection.find({}, {"password": 0}))  # Exclure les mots de passe
        
        # Convertir ObjectId en string
        serialized_users = [serialize_user(user) for user in users]

        
        return {
            "users": serialized_users,
            "total": len(users)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des utilisateurs: {str(e)}"
        )

@router.get("/users/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer un utilisateur par ID"""
    
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de base de données non disponible"
        )
    
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        return serialize_user(user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'utilisateur: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Supprimer un utilisateur"""
    
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de base de données non disponible"
        )
    
    try:
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        return {"message": "Utilisateur supprimé avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

# Endpoint de santé
@router.get("/health")
async def health_check():
    """Vérification de l'état de l'API et de la base de données"""
    
    mongodb_status = "connecté" if users_collection is not None else "déconnecté"
    
    return {
        "status": "actif",
        "mongodb": mongodb_status,
        "timestamp": datetime.utcnow().isoformat()
    }
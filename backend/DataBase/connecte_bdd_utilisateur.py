from pymongo import MongoClient
from passlib.context import CryptContext
import os
from bson import ObjectId

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration MongoDB pour Docker
# Utilise la variable d'environnement ou une valeur par défaut
MONGODB_URL = 'mongodb://admin:powerai123@mongodb:27017/Projet_NLP_&_CV?authSource=admin'
DATABASE_NAME = "Projet_NLP_&_CV"  # Votre base de données existante
COLLECTION_NAME = "utilisateurs"  # Votre collection existante

# Connexion MongoDB avec gestion d'erreur améliorée
try:
    client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    # Test de la connexion
    client.server_info()
    db = client[DATABASE_NAME]
    users_collection = db[COLLECTION_NAME]
    print("✅ Connexion à MongoDB réussie")
    print(f"   - URL: {MONGODB_URL}")
    print(f"   - Base: {DATABASE_NAME}")
    print(f"   - Collection: {COLLECTION_NAME}")
except Exception as e:
    print(f"❌ Erreur de connexion à MongoDB: {e}")
    # Optionnel: continuer sans MongoDB pour le développement
    client = None
    db = None
    users_collection = None

# Fonctions utilitaires
def hash_password(password: str) -> str:
    """Hache le mot de passe"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie le mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)

def user_exists(username: str = None, email: str = None) -> bool:
    """Vérifie si l'utilisateur existe déjà"""
    if users_collection is None:
        raise Exception("Connexion MongoDB non disponible")
    
    # Construction de la requête
    conditions = []
    if username:
        conditions.append({"username": username})
    if email:
        conditions.append({"email": email})
    
    if not conditions:
        return False
    
    # Utiliser $or seulement s'il y a plusieurs conditions
    if len(conditions) == 1:
        query = conditions[0]
    else:
        query = {"$or": conditions}
    
    return users_collection.find_one(query) is not None

def get_database_stats():
    """Obtenir des statistiques sur la base de données"""
    if db is None:
        return {"error": "Connexion MongoDB non disponible"}
    
    try:
        stats = db.command("dbstats")
        collections = db.list_collection_names()
        
        return {
            "database": DATABASE_NAME,
            "collections": collections,
            "dataSize": stats.get("dataSize", 0),
            "storageSize": stats.get("storageSize", 0),
            "indexes": stats.get("indexes", 0),
            "objects": stats.get("objects", 0)
        }
    except Exception as e:
        return {"error": str(e)}
    

def user_exists_exclude_id(user_id: str, username: str = None, email: str = None) -> bool:
    """Vérifie si l'utilisateur existe déjà (en excluant l'ID actuel)"""
    if users_collection is None:
        raise Exception("Connexion MongoDB non disponible")
    
    conditions = []
    if username:
        conditions.append({"username": username})
    if email:
        conditions.append({"email": email})
    
    if not conditions:
        return False
    
    # Exclure l'utilisateur actuel de la recherche
    if len(conditions) == 1:
        query = {"$and": [conditions[0], {"_id": {"$ne": ObjectId(user_id)}}]}
    else:
        query = {"$and": [{"$or": conditions}, {"_id": {"$ne": ObjectId(user_id)}}]}
    
    return users_collection.find_one(query) is not None
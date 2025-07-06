from pymongo import MongoClient
from passlib.context import CryptContext
import os
from bson import ObjectId
from datetime import datetime

# Configuration MongoDB pour Docker
# Utilise la variable d'environnement ou une valeur par défaut
MONGODB_URL = 'mongodb://admin:powerai123@mongodb:27017/Projet_NLP_&_CV?authSource=admin'
DATABASE_NAME = "Projet_NLP_&_CV"  # Votre base de données existante
COLLECTION_NAME = "Models_IA"  # Votre collection existante

# Connexion MongoDB avec gestion d'erreur améliorée
try:
    client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    # Test de la connexion
    client.server_info()
    db = client[DATABASE_NAME]
    models_collection  = db[COLLECTION_NAME]
    print("✅ Connexion à MongoDB réussie")
    print(f"   - URL: {MONGODB_URL}")
    print(f"   - Base: {DATABASE_NAME}")
    print(f"   - Collection Models IA: {COLLECTION_NAME}")
except Exception as e:
    print(f"❌ Erreur de connexion à MongoDB: {e}")
    # Optionnel: continuer sans MongoDB pour le développement
    client = None
    db = None
    users_collection = None



# Fonction utilitaire pour sauvegarder les résultats du modèle
def save_model_result(user_id: str, image_info: dict, model_params: dict, results: dict, processing: dict):
    """Sauvegarde le résultat d'une génération de caption dans MongoDB"""
    if models_collection is None:
        return None
    
    try:
        document = {
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "image_info": image_info,
            "model_params": model_params,
            "results": results,
            "processing": processing
        }
        result = models_collection.insert_one(document)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Erreur sauvegarde: {e}")
        return None
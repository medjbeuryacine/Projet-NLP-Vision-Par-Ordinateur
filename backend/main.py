from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# import routes
from routes.gestion_utilisateur import router as user_router
from routes.model_routes import router as caption_router

from models_stable_v2.model_loader import initialize_caption_generator


# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Et modifier la création de l'app :
app = FastAPI(
    title="API Complète - Utilisateurs + Modèles IA",
    description="API pour la gestion des utilisateurs et la génération de captions d'images",
    version="2.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mets ici l'URL de ton frontend au lieu de "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# routes
app.include_router(user_router)
app.include_router(caption_router)


@app.on_event("startup")
async def startup_event():
    try:
        initialize_caption_generator("/app/models_stable_v2/best_model_v2.pth")
        logger.info("Modèle chargé avec succès au démarrage")
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle: {e}")

@app.get("/", tags=["Info API"])
async def root():
    from models_stable_v2.model_loader import get_caption_generator
   
    caption_generator = get_caption_generator()
    model_status = "loaded" if caption_generator and caption_generator.is_loaded() else "not_loaded"
    
    return {
        "message": "PowerAI - API Complète",
        "status": "actif",
        "version": "2.0.0",
        "model_status": model_status,
        "endpoints": {
            "documentation": "/docs",
            "utilisateurs": {
                "créer": "/users/create",
                "connexion": "/users/login",
                "liste": "/users/list",
                "profil": "/users/{user_id}",
                "modifier": "/users/{user_id}",
                "supprimer": "/users/{user_id}"
            },
            "modèle_ia": {
               "caption_unique": "/generate_caption",
               "caption_batch": "/generate_caption_batch",
               "infos": "/model_info"
           }
        }
    }

@app.get("/health", tags=["Info API"])
async def health_check():
    from models_stable_v2.model_loader import get_caption_generator
    
    # Vérifier le modèle
    caption_generator = get_caption_generator()
    model_status = "loaded" if caption_generator and caption_generator.is_loaded() else "not_loaded"
    
    return {
        "status": "healthy",
        "api_version": "2.0.0",
        "services": {
            "mongodb": "connected",  # À vérifier dynamiquement si nécessaire
            "model": model_status
        }
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
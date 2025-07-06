from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
from models_stable_v2.model_loader import get_caption_generator, initialize_caption_generator
from PIL import Image
import io
from security.auth import get_current_user
from utils.translator import translate_to_french
from utils.emojis import add_emojis_to_text
from DataBase.connecte_bdd_model import save_model_result
from datetime import datetime
import time

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialiser FastAPI
router = APIRouter(tags=["AI Models"])

# Variable globale pour le générateur
caption_generator = None

@router.post("/generate_caption")
async def generate_caption(
    file: UploadFile = File(...),
    beam_width: int = 3,
    max_length: int = 20,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    caption_generator = get_caption_generator()
    if caption_generator is None:
        raise HTTPException(status_code=500, detail="Modèle non chargé")
    
    # Vérifier le type de fichier
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")
    
    try:
        # Lire et traiter l'image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convertir en RGB si nécessaire
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Générer la caption
        caption_en = caption_generator.generate_caption(
            image, beam_width=beam_width, max_length=max_length
        )

        caption_fr = translate_to_french(caption_en)

        # Ajouter des emojis
        caption_with_emojis = add_emojis_to_text(caption_fr)

        # sauvegarder dans la Base de Données 
        try:
            save_model_result(
                user_id=current_user["id"],
                image_info={
                    "filename": file.filename,
                    "size": f"{image.size[0]}x{image.size[1]}",
                    "format": image.format
                },
                model_params={
                    "beam_width": beam_width,
                    "max_length": max_length,
                    "model_version": "best_model_v2.pth"
                },
                results={
                    "caption_original": caption_en,
                    "caption_french": caption_fr,
                    "caption_final": caption_with_emojis
                },
                processing={
                    "device": str(caption_generator.device),
                    "success": True
                }
            )
        except Exception as e:
            logger.warning(f"Erreur sauvegarde DB: {e}")

        return {
            "success": True,
            "caption_final": caption_with_emojis,
            "caption_french": caption_fr,
            "caption_original": caption_en,
            "filename": file.filename,
            "image_size": f"{image.size[0]}x{image.size[1]}",
            "beam_width": beam_width,
            "max_length": max_length,
            "model_used": "best_model_v2.pth"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")

@router.post("/generate_caption_batch")
async def generate_caption_batch(
    files: list[UploadFile] = File(...),
    beam_width: int = 3,
    max_length: int = 20,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    if caption_generator is None:
        raise HTTPException(status_code=500, detail="Modèle non chargé")
    
    if len(files) > 10:  # Limiter le nombre d'images
        raise HTTPException(status_code=400, detail="Maximum 10 images par batch")
    
    results = []
    
    for file in files:
        if not file.content_type.startswith("image/"):
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "Le fichier doit être une image"
            })
            continue
        
        try:
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            caption_en = caption_generator.generate_caption(
                image, beam_width=beam_width, max_length=max_length
            )
            
            # Traduire en français
            caption_fr = translate_to_french(caption_en)

            # Ajouter des emojis
            caption_with_emojis = add_emojis_to_text(caption_fr)

            # Sauvegarder chaque résultat en base (après le try/except de traitement d'image)
            try:
                save_model_result(
                    user_id=current_user["id"],
                    image_info={
                        "filename": file.filename,
                        "size": f"{image.size[0]}x{image.size[1]}",
                        "format": image.format
                    },
                    model_params={
                        "beam_width": beam_width,
                        "max_length": max_length,
                        "model_version": "best_model_v2.pth"
                    },
                    results={
                        "caption_original": caption_en,
                        "caption_french": caption_fr,
                        "caption_final": caption_with_emojis
                    },
                    processing={
                        "device": str(caption_generator.device),
                        "success": True
                    }
                )
            except Exception as e:
                logger.warning(f"Erreur sauvegarde DB pour {file.filename}: {e}")

            results.append({
                "filename": file.filename,
                "success": True,
                "caption_final": caption_with_emojis,
                "caption_french": caption_fr,
                "caption_original": caption_en,
                "image_size": f"{image.size[0]}x{image.size[1]}"
            })
            
        except Exception as e:
            logger.error(f"Erreur pour {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return {
        "success": True,
        "total_images": len(files),
        "results": results,
        "beam_width": beam_width,
        "max_length": max_length,
        "model_used": "best_model_v2.pth"
    }

@router.get("/model_info")
async def model_info(current_user: dict = Depends(get_current_user)):
    if caption_generator is None:
        raise HTTPException(status_code=500, detail="Modèle non chargé")
    
    return {
        "device": str(caption_generator.device),
        "vocab_size": len(caption_generator.word_to_idx),
        "model_architecture": "ResNet-50 + LSTM + Attention",
        "model_file": "best_model_v2.pth",
        "available": True
    }
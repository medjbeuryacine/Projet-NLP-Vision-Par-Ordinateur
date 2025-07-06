from googletrans import Translator
import logging

logger = logging.getLogger(__name__)

# Initialiser le traducteur
translator = Translator()

def translate_to_french(text: str) -> str:
    """
    Traduit un texte anglais vers le français
    
    Args:
        text (str): Texte en anglais à traduire
        
    Returns:
        str: Texte traduit en français
    """
    try:
        result = translator.translate(text, src='en', dest='fr')
        return result.text
    except Exception as e:
        logger.warning(f"Erreur de traduction: {e}")
        return text  # Retourner le texte original en cas d'erreur

def translate_text(text: str, source_lang: str = 'en', target_lang: str = 'fr') -> str:
    """
    Fonction générique de traduction
    
    Args:
        text (str): Texte à traduire
        source_lang (str): Langue source (défaut: 'en')
        target_lang (str): Langue cible (défaut: 'fr')
        
    Returns:
        str: Texte traduit
    """
    try:
        result = translator.translate(text, src=source_lang, dest=target_lang)
        return result.text
    except Exception as e:
        logger.warning(f"Erreur de traduction {source_lang}->{target_lang}: {e}")
        return text
    



#################################################### sans wifi ################################################
# from transformers import pipeline
# import logging

# logger = logging.getLogger(__name__)

# # Initialiser le modèle de traduction local (une seule fois)
# try:
#     translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr", device=-1)
#     logger.info("Modèle de traduction local chargé")
# except Exception as e:
#     logger.error(f"Erreur chargement modèle de traduction: {e}")
#     translator = None

# def translate_to_french(text: str) -> str:
#     """
#     Traduit un texte anglais vers le français (HORS LIGNE)
#     """
#     if translator is None:
#         logger.warning("Traducteur non disponible, retour du texte original")
#         return text
    
#     try:
#         result = translator(text, max_length=512)
#         return result[0]['translation_text']
#     except Exception as e:
#         logger.warning(f"Erreur de traduction locale: {e}")
#         return text
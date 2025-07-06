import re
import logging

logger = logging.getLogger(__name__)

# Dictionnaire de mots-clés vers emojis
EMOJI_MAPPING = {
    # Animaux domestiques
    'chat': '🐱', 'chats': '🐱', 'chaton': '🐱', 'chatons': '🐱',
    'chien': '🐶', 'chiens': '🐶', 'chiot': '🐶', 'chiots': '🐶',
    'oiseau': '🐦', 'oiseaux': '🐦', 'pigeon': '🐦', 'pigeons': '🐦',
    'poisson': '🐟', 'poissons': '🐟',
    'lapin': '🐰', 'lapins': '🐰',
    'hamster': '🐹', 'souris': '🐭',
    
    # Animaux sauvages
    'éléphant': '🐘', 'éléphants': '🐘',
    'lion': '🦁', 'lions': '🦁', 'lionne': '🦁',
    'tigre': '🐅', 'tigres': '🐅',
    'ours': '🐻', 'panda': '🐼',
    'singe': '🐵', 'singes': '🐵',
    'girafe': '🦒', 'girafes': '🦒',
    'zèbre': '🦓', 'rhinocéros': '🦏',
    'hippopotame': '🦛', 'crocodile': '🐊',
    'serpent': '🐍', 'serpents': '🐍',
    'papillon': '🦋', 'papillons': '🦋',
    'abeille': '🐝', 'abeilles': '🐝',
    
    # Animaux de ferme
    'vache': '🐄', 'vaches': '🐄',
    'cochon': '🐷', 'cochons': '🐷', 'porc': '🐷',
    'mouton': '🐑', 'moutons': '🐑',
    'chèvre': '🐐', 'chèvres': '🐐',
    'coq': '🐓', 'poule': '🐔', 'poules': '🐔',
    'canard': '🦆', 'canards': '🦆',
    'cheval': '🐴', 'chevaux': '🐴', 'poney': '🐴',
    
    # Nourriture - Fruits
    'pomme': '🍎', 'pommes': '🍎',
    'banane': '🍌', 'bananes': '🍌',
    'orange': '🍊', 'oranges': '🍊',
    'citron': '🍋', 'citrons': '🍋',
    'raisin': '🍇', 'raisins': '🍇',
    'fraise': '🍓', 'fraises': '🍓',
    'pastèque': '🍉', 'melon': '🍈',
    'pêche': '🍑', 'pêches': '🍑',
    'ananas': '🍍', 'cerise': '🍒', 'cerises': '🍒',
    
    # Nourriture - Plats
    'pizza': '🍕', 'burger': '🍔', 'hamburger': '🍔',
    'frites': '🍟', 'sandwich': '🥪', 'sandwichs': '🥪',
    'salade': '🥗', 'salades': '🥗',
    'soupe': '🍲', 'pâtes': '🍝', 'spaghetti': '🍝',
    'riz': '🍚', 'pain': '🍞', 'croissant': '🥐',
    'taco': '🌮', 'sushi': '🍣', 'ramen': '🍜',
    
    # Nourriture - Desserts
    'gâteau': '🍰', 'gâteaux': '🍰',
    'tarte': '🥧', 'tartes': '🥧',
    'glace': '🍦', 'glaces': '🍦',
    'bonbon': '🍬', 'bonbons': '🍬',
    'chocolat': '🍫', 'cookie': '🍪', 'cookies': '🍪',
    'donuts': '🍩', 'muffin': '🧁',
    
    # Boissons
    'café': '☕', 'thé': '🍵',
    'bière': '🍺', 'bières': '🍺',
    'vin': '🍷', 'champagne': '🍾',
    'cocktail': '🍹', 'jus': '🧃',
    'lait': '🥛', 'eau': '💧',
    
    # Transport
    'voiture': '🚗', 'voitures': '🚗', 'auto': '🚗',
    'vélo': '🚲', 'vélos': '🚲', 'bicyclette': '🚲',
    'moto': '🏍️', 'motos': '🏍️', 'scooter': '🛵',
    'avion': '✈️', 'avions': '✈️',
    'train': '🚂', 'trains': '🚂',
    'bateau': '⛵', 'bateaux': '⛵', 'navire': '🚢',
    'bus': '🚌', 'taxi': '🚕',
    'camion': '🚛', 'camions': '🚛',
    'métro': '🚇', 'tramway': '🚊',
    
    # Nature - Météo
    'soleil': '☀️', 'nuage': '☁️', 'nuages': '☁️',
    'pluie': '🌧️', 'orage': '⛈️',
    'neige': '❄️', 'vent': '💨',
    'arc-en-ciel': '🌈', 'étoile': '⭐', 'étoiles': '⭐',
    'lune': '🌙', 'ciel': '🌌',
    
    # Nature - Paysages
    'montagne': '🏔️', 'montagnes': '🏔️',
    'mer': '🌊', 'océan': '🌊', 'plage': '🏖️',
    'forêt': '🌲', 'forêts': '🌲',
    'désert': '🏜️', 'volcan': '🌋',
    'lac': '🏞️', 'rivière': '🏞️',
    'cascade': '🌊', 'île': '🏝️',
    
    # Nature - Végétation
    'fleur': '🌸', 'fleurs': '🌸',
    'rose': '🌹', 'roses': '🌹',
    'tournesol': '🌻', 'tulipe': '🌷',
    'arbre': '🌳', 'arbres': '🌳',
    'palmier': '🌴', 'palmiers': '🌴',
    'herbe': '🌱', 'feuille': '🍃', 'feuilles': '🍃',
    'champignon': '🍄', 'champignons': '🍄',
    
    # Personnes et parties du corps
    'personne': '👤', 'personnes': '👥', 'gens': '👥',
    'homme': '👨', 'hommes': '👨', 'garçon': '👦',
    'femme': '👩', 'femmes': '👩', 'fille': '👧',
    'enfant': '👶', 'enfants': '👶', 'bébé': '👶',
    'famille': '👨‍👩‍👧‍👦', 'couple': '👫',
    'visage': '😊', 'œil': '👁️', 'yeux': '👀',
    'main': '✋', 'mains': '👐', 'doigt': '👆',
    'pied': '🦶', 'pieds': '🦶',
    
    # Émotions et expressions
    'sourire': '😊', 'rire': '😄', 'joie': '😃',
    'triste': '😢', 'tristesse': '😢', 'pleur': '😭',
    'colère': '😠', 'surpris': '😲', 'surprise': '😲',
    'amour': '❤️', 'cœur': '❤️', 'bisou': '😘',
    'fatigue': '😴', 'fatigué': '😴',
    'peur': '😨', 'inquiet': '😰',
    
    # Actions et activités
    'jouer': '🎮', 'jeu': '🎮', 'sport': '⚽',
    'dormir': '😴', 'sommeil': '😴',
    'manger': '🍴', 'boire': '🥤',
    'courir': '🏃', 'marcher': '🚶', 'danser': '💃',
    'nager': '🏊', 'natation': '🏊',
    'lire': '📖', 'lecture': '📖',
    'écrire': '✍️', 'écriture': '✍️',
    'cuisiner': '👨‍🍳', 'cuisine': '👨‍🍳',
    'travail': '💼', 'travailler': '💼',
    'étudier': '📚', 'étude': '📚',
    'voyage': '✈️', 'voyager': '✈️',
    
    # Objets du quotidien
    'livre': '📚', 'livres': '📚',
    'téléphone': '📱', 'portable': '📱',
    'ordinateur': '💻', 'clavier': '⌨️',
    'télé': '📺', 'télévision': '📺',
    'radio': '📻', 'musique': '🎵',
    'appareil photo': '📷', 'photo': '📸',
    'montre': '⌚', 'lunettes': '👓',
    'sac': '👜', 'sacs': '👜',
    'parapluie': '☂️', 'chapeau': '👒',
    'clé': '🔑', 'clés': '🔑',
    'argent': '💰', 'euro': '💶',
    
    # Lieux et bâtiments
    'maison': '🏠', 'maisons': '🏠', 'domicile': '🏠',
    'appartement': '🏢', 'immeuble': '🏢',
    'école': '🏫', 'écoles': '🏫',
    'hôpital': '🏥', 'pharmacie': '💊',
    'magasin': '🏪', 'supermarché': '🏪',
    'restaurant': '🍽️', 'café': '☕',
    'église': '⛪', 'mosquée': '🕌',
    'parc': '🌳', 'jardin': '🌻',
    'piscine': '🏊', 'stade': '🏟️',
    'aéroport': '✈️', 'gare': '🚂',
    
    # Vêtements
    'vêtement': '👕', 'vêtements': '👕',
    'tshirt': '👕', 'chemise': '👔',
    'pantalon': '👖', 'jean': '👖',
    'robe': '👗', 'jupe': '👗',
    'chaussure': '👟', 'chaussures': '👟',
    'basket': '👟', 'bottes': '👢',
    'manteau': '🧥', 'veste': '🧥',
    'pull': '🧥', 'sweat': '🧥',
    
    # Couleurs
    'rouge': '🔴', 'bleu': '🔵', 'vert': '🟢',
    'jaune': '🟡', 'orange': '🟠', 'violet': '🟣',
    'rose': '🌸', 'blanc': '⚪', 'noir': '⚫',
    'gris': '🔘', 'marron': '🤎',
    
    # Objets techniques
    'wifi': '📶', 'internet': '🌐',
    'batterie': '🔋', 'électricité': '⚡',
    'ampoule': '💡', 'lampe': '💡',
    'micro': '🎤', 'casque': '🎧',
    'caméra': '📹', 'film': '🎬',
    
    # Symboles et concepts
    'temps': '⏰', 'heure': '🕐',
    'calendrier': '📅', 'date': '📅',
    'fête': '🎉', 'anniversaire': '🎂',
    'cadeau': '🎁', 'surprise': '🎁',
    'feu': '🔥', 'flamme': '🔥',
    'eau': '💧', 'glace': '🧊',
    'diamant': '💎', 'or': '🏆',
    'médaille': '🥇', 'trophée': '🏆',
    'drapeau': '🏳️', 'france': '🇫🇷',
    
    # Nombres (bonus)
    'un': '1️⃣', 'deux': '2️⃣', 'trois': '3️⃣',
    'quatre': '4️⃣', 'cinq': '5️⃣', 'six': '6️⃣',
    'sept': '7️⃣', 'huit': '8️⃣', 'neuf': '9️⃣',
    'dix': '🔟', 'cent': '💯',
    
    # Directions
    'gauche': '⬅️', 'droite': '➡️',
    'haut': '⬆️', 'bas': '⬇️',
    'nord': '⬆️', 'sud': '⬇️',
    'est': '➡️', 'ouest': '⬅️',

    # Personnes et parties du corps
    'personne': '👤', 'personnes': '👥', 'gens': '👥',
    'homme': '👨', 'hommes': '👨', 'garçon': '👦',
    'femme': '👩', 'femmes': '👩', 'fille': '👧',
    'enfant': '👶', 'enfants': '👶', 'bébé': '👶',
    'famille': '👨‍👩‍👧‍👦', 'couple': '👫',
    'visage': '😊', 'œil': '👁️', 'yeux': '👀',
    'main': '✋', 'mains': '👐', 'doigt': '👆',
    'pied': '🦶', 'pieds': '🦶',
}

def add_emojis_to_text(text: str) -> str:
    """
    Ajoute des emojis pertinents à un texte basé sur les mots-clés
    
    Args:
        text (str): Texte à enrichir avec des emojis
        
    Returns:
        str: Texte avec emojis ajoutés
    """
    try:
        # Convertir en minuscules pour la recherche
        text_lower = text.lower()
        words = text_lower.split()
        
        # Trouver les emojis correspondants
        found_emojis = set()
        
        for word in words:
            # Recherche exacte
            if word in EMOJI_MAPPING:
                found_emojis.add(EMOJI_MAPPING[word])
            
            # Recherche dans les mots composés
            for key, emoji in EMOJI_MAPPING.items():
                if key in text_lower:
                    found_emojis.add(emoji)
        
        # Limiter à 3 emojis max pour éviter la surcharge
        emojis_to_add = list(found_emojis)[:3]
        
        if emojis_to_add:
            return f"{text} {' '.join(emojis_to_add)}"
        else:
            return text
            
    except Exception as e:
        logger.warning(f"Erreur lors de l'ajout d'emojis: {e}")
        return text

def smart_emoji_placement(text: str) -> str:
    """
    Place les emojis de manière plus intelligente dans le texte
    """
    try:
        text_lower = text.lower()
        result = text
        
        # Remplacer directement certains mots par mot + emoji
        for keyword, emoji in EMOJI_MAPPING.items():
            if keyword in text_lower:
                # Utiliser regex pour remplacer le mot en gardant la casse
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                result = pattern.sub(f"{keyword} {emoji}", result, count=1)
                break  # Un seul remplacement pour éviter la surcharge
        
        return result
        
    except Exception as e:
        logger.warning(f"Erreur placement intelligent emojis: {e}")
        return text
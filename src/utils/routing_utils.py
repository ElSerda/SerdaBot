"""Routing utilities for proactive message routing.

Simple regex-based detection functions to determine if a message should be
routed to specific tools BEFORE calling the LLM.

Design principles:
- Fast (< 1ms each)
- No LLM calls
- No external dependencies
- Reusable across the codebase
- Focus on INTENT, not grammar (avoid false positives from verb tenses)
"""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular import for type hints
    pass


def contains_game_context(text: str) -> bool:
    """Détecte si le message contient un contexte de jeu vidéo.
    
    Args:
        text: User message text
        
    Returns:
        True if game-related keywords detected, False otherwise
        
    Examples:
        >>> contains_game_context("Zelda sort quand ?")
        True
        >>> contains_game_context("GTA 6 c'est sur PC ?")
        True
        >>> contains_game_context("Salut ça va ?")
        False
    """
    text_lower = text.lower()
    
    # Mots-clés jeux vidéo (génériques, pas de liste de jeux hardcodée)
    game_keywords = [
        r'\bjeu\b',           # "le jeu", "un jeu"
        r'\bgame\b',          # "game"
        r'\bsorti\b',         # "sorti", "sortira"
        r'\bsortir\b',        # "va sortir"
        r'\bsortie\b',        # "date de sortie"
        r'\bplateforme\b',    # "plateforme"
        r'\bpc\b',            # "sur pc"
        r'\bps[0-9]\b',       # "ps4", "ps5"
        r'\bxbox\b',          # "xbox"
        r'\bswitch\b',        # "nintendo switch"
        r'\bsteam\b',         # "steam"
        r'\bdispo\b',         # "dispo", "disponible"
        r'\bdisponible\b',
        r'\bjouer\b',         # "jouer à"
    ]
    
    for pattern in game_keywords:
        if re.search(pattern, text_lower):
            return True
    
    return False


def contains_date_or_release_question(text: str) -> bool:
    """Détecte si le message pose une question sur une date ou sortie de jeu.
    
    Focus sur l'INTENTION (questions de date/sortie), pas sur le temps verbal.
    Évite les faux positifs du style "J'ai adoré Elden Ring" (passé ≠ question).
    
    Args:
        text: User message text
        
    Returns:
        True if date/release question detected, False otherwise
        
    Examples:
        >>> contains_date_or_release_question("Zelda sort en 2025 ?")
        True
        >>> contains_date_or_release_question("Quand est sorti GTA 5 ?")
        True
        >>> contains_date_or_release_question("GTA 6 c'est pour quand ?")
        True
        >>> contains_date_or_release_question("J'ai adoré Elden Ring")
        False
        >>> contains_date_or_release_question("Tu as joué à Cyberpunk ?")
        False
    """
    text_lower = text.lower()
    
    # === 1. Mots-clés de QUESTION sur date/sortie (high confidence) ===
    release_question_keywords = [
        r'\bquand\b',                 # "quand ?", "c'est quand", "pour quand"
        r'\bdate\b',                  # "date de sortie", "quelle date"
        r'\bsorti\b',                 # "est sorti", "sort quand"
        r'\bsortir\b',                # "va sortir", "doit sortir"
        r'\bsortie\b',                # "date de sortie"
        r'\breleas(e|ed)\b',          # "release date", "released"
        r'\bdisponible\b',            # "disponible quand"
        r'\bdispo\b',                 # "dispo quand"
    ]
    
    for pattern in release_question_keywords:
        if re.search(pattern, text_lower):
            return True
    
    # === 2. Années explicites (2024+) ===
    # Si l'utilisateur mentionne une année future, c'est probablement une question de date
    if re.search(r'\b202[4-9]\b|\b20[3-9][0-9]\b', text):
        return True
    
    # === 3. Expressions temporelles futures ===
    future_time_keywords = [
        r'\bcette ann[ée]e\b',        # "cette année"
        r'\bl\'?an prochain\b',       # "l'an prochain"
        r'\bprochain\b',              # "prochain"
        r'\bprochainement\b',         # "prochainement"
        r'\bbient[ôo]t\b',           # "bientôt"
        r'\bjanvier\b', r'\bf[ée]vrier\b', r'\bmars\b',
        r'\bavril\b', r'\bmai\b', r'\bjuin\b',
        r'\bjuillet\b', r'\baout\b', r'\bao[ûu]t\b',
        r'\bseptembre\b', r'\boctobre\b', r'\bnovembre\b', r'\bd[ée]cembre\b',
    ]
    
    for pattern in future_time_keywords:
        if re.search(pattern, text_lower):
            return True
    
    return False


async def should_route_to_gameinfo(user_msg: str) -> str | None:
    """Détermine si le message doit être routé vers gameinfo AVANT appel LLM.
    
    Logique proactive SIMPLE (KISS) :
    1. Si question de date/sortie détectée → extraire nom du jeu
    2. Si nom trouvé ET valide → return game_name
    3. Sinon → return None
    
    Args:
        user_msg: User message text
        
    Returns:
        str: Game name to route to gameinfo
        None: No routing needed
        
    Examples:
        >>> await should_route_to_gameinfo("Quand sort le prochain Zelda ?")
        "zelda"
        >>> await should_route_to_gameinfo("Date de sortie ?")
        None
    """
    # Étape 1 : Vérifier si c'est une question de date/sortie
    if not contains_date_or_release_question(user_msg):
        return None
    
    # Étape 2 : Extraction SIMPLE par patterns (4 patterns optimisés)
    # Lowercase pour éviter faux positifs sur mots en début de phrase (ex: "Quand")
    msg_lower = user_msg.lower()
    
    # Pattern 1: "prochain/dernier NomPropre" (ex: "prochain Zelda")
    match = re.search(r'(?:prochain|dernier|nouveau)\s+(?:le\s+)?([a-z][a-z0-9\s]+?)(?:\s+\?|$)', msg_lower)
    if match:
        name = match.group(1).strip()
        if len(name) > 2 and name not in ['jeu', 'game', 'le', 'la', 'les']:
            return name
    
    # Pattern 2: "NomPropre (sort|sorti|dispo)" (ex: "Zelda sort quand")
    match = re.search(r'([a-z][a-z0-9\s]+?)\s+(?:sort|sorti|dispo)', msg_lower)
    if match:
        name = match.group(1).strip()
        if len(name) > 2 and 'date de' not in name and name not in ['le', 'la', 'les', 'quand', 'pour']:
            return name
    
    # Pattern 3: "date de sortie NomPropre" (ex: "Date de sortie Elden Ring")
    match = re.search(r'date de sortie\s+([a-z][a-z0-9\s]+?)(?:\s+\?|$)', msg_lower)
    if match:
        name = match.group(1).strip()
        if len(name) > 2:
            return name
    
    # Pattern 4: "202X pour NomPropre" (ex: "2025 pour GTA")
    match = re.search(r'202[0-9]\s+pour\s+([a-z][a-z0-9\s]+?)(?:\s+\?|$)', msg_lower)
    if match:
        name = match.group(1).strip()
        if len(name) > 2:
            return name
    
    # Pas de nom trouvé
    return None

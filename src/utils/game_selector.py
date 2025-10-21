# src/utils/game_selector.py
"""Matching de sélection utilisateur pour jeux multiples."""

import re
from typing import Dict, List, Optional

from unidecode import unidecode


def normalize(text: str) -> str:
    """Normalise: accents, casse, espaces."""
    return unidecode(text).casefold().strip()


def match_selection(user_text: str, games: List[Dict]) -> Optional[Dict]:
    """
    Parse la sélection user. Cascade:
    1. Numéro explicite ("1", "le 2", "2ème")
    2. Ordinal ("premier", "second", "first")
    3. Sous-chaîne numérique dans nom ("2077", "3")
    4. Fuzzy match titre (ratio ≥ 80%)
    
    Args:
        user_text: Texte de l'utilisateur
        games: Liste de dicts {name, year, platforms, ...}
    
    Returns:
        Le jeu matché ou None
    """
    if not games:
        return None
    
    normalized = normalize(user_text)
    
    # 1. Numéro direct
    num_match = re.search(r'\b(\d{1,2})\b', normalized)
    if num_match:
        idx = int(num_match.group(1)) - 1
        if 0 <= idx < len(games):
            return games[idx]
    
    # 2. Ordinal FR/EN
    ordinals = {
        "premier": 0, "deuxieme": 1, "troisieme": 2, "quatrieme": 3, "cinquieme": 4,
        "first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4,
        "1er": 0, "2eme": 1, "3eme": 2, "2nd": 1, "3rd": 2
    }
    for word, idx in ordinals.items():
        if word in normalized and idx < len(games):
            return games[idx]
    
    # 3. Sous-chaîne numérique (année/numéro dans titre)
    year_match = re.search(r'\b(19|20)\d{2}\b|\b\d{3,4}\b', user_text)
    if year_match:
        num_str = year_match.group(0)
        for game in games:
            if num_str in normalize(game["name"]) or num_str == str(game.get("year", "")):
                return game
    
    # 4. Fuzzy match titre (simple ratio sans lib externe)
    # On calcule un score basique de similarité
    best_game = None
    best_score = 0
    
    for game in games:
        game_name_norm = normalize(game["name"])
        # Score simple: nombre de mots communs / total de mots
        user_words = set(normalized.split())
        game_words = set(game_name_norm.split())
        
        if not user_words or not game_words:
            continue
        
        common = len(user_words & game_words)
        total = len(user_words | game_words)
        score = (common / total) * 100 if total > 0 else 0
        
        # Bonus si user_text est substring du nom
        if normalized in game_name_norm:
            score += 30
        
        if score > best_score:
            best_score = score
            best_game = game
    
    # Seuil de 60% (plus permissif que fuzzy 80% car notre algo est simple)
    if best_score >= 60:
        return best_game
    
    return None

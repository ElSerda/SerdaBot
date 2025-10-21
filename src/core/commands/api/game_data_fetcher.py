"""
Game Data Fetcher - Gestionnaire centralisé des sources de données de jeux.

Ce module orchestre les différentes APIs pour récupérer les informations
sur les jeux vidéo avec un système de priorité et fallback.

Priorité des sources :
    1. Cache (si disponible)
    2. RAWG (source principale - la plus complète et à jour)
    3. Steam (fallback pour jeux indie/récents absents de RAWG)
    4. IGDB API (fallback si RAWG et Steam échouent)
    5. IGDB Web scraping (dernier recours)
"""
from typing import Dict, Optional

from core.cache import GAME_CACHE, get_cache_key, get_ttl_for_game

from .igdb_api import get_igdb_token, query_game, search_igdb_web
from .rawg_api import fetch_game_from_rawg
from .steam_api import fetch_game_from_steam


async def fetch_game_data(game_name: str, config: dict, cache_only: bool = False) -> Optional[Dict]:
    """
    Point d'entrée UNIQUE pour récupérer des données de jeu.
    
    Stratégie de recherche parallèle intelligente :
        1. Cache (si disponible)
        2. Extraction année de la requête (ex: "Cyberpunk 2077" → 2077)
        3. RAWG + Steam en parallèle
        4. Scoring contextuel (similarité + qualité + année utilisateur)
        5. Retour du meilleur match
        6. Fallback IGDB si aucun résultat satisfaisant
    
    Args:
        game_name: Nom du jeu à rechercher (peut inclure année: "Hades 2")
        config: Configuration globale du bot
        cache_only: Si True, retourne uniquement depuis le cache (tests)
    
    Returns:
        Dict avec les données du jeu (format normalisé), ou None si non trouvé.
    """
    print(f"[GAME-DATA] 🔍 Recherche de '{game_name}'...")
    
    # 🔍 ÉTAPE 0 : Vérifier le cache
    cache_key = get_cache_key("gamedata", game_name)
    cached_data = GAME_CACHE.get(cache_key)
    
    if cached_data:
        print(f"[GAME-DATA] ⚡ CACHE HIT: {cached_data['name']}")
        return cached_data
    
    # Mode cache only pour les tests (skip API)
    if cache_only:
        print("[GAME-DATA] ⚠️ Mode CACHE ONLY: Jeu non trouvé dans le cache")
        return None
    
    # 📅 ÉTAPE 0.5 : Extraire l'année de la requête utilisateur (si présente)
    user_year = _extract_year_from_query(game_name)
    if user_year:
        print(f"[GAME-DATA] 📅 Année détectée dans la requête: {user_year}")
    
    # 🎮 ÉTAPE 1 : Requêtes parallèles RAWG + Steam
    print("[GAME-DATA] 📡 Requêtes parallèles: RAWG + Steam...")
    
    import asyncio
    
    # Lancer les 2 recherches en parallèle
    rawg_task = fetch_game_from_rawg(game_name, config, user_year=user_year)
    steam_task = fetch_game_from_steam(game_name)
    
    rawg_data, steam_data = await asyncio.gather(
        rawg_task,
        steam_task,
        return_exceptions=True  # Ne pas crasher si une API échoue
    )
    
    # Gérer les exceptions
    if isinstance(rawg_data, Exception):
        print(f"[GAME-DATA] ❌ RAWG erreur: {rawg_data}")
        rawg_data = None
    
    if isinstance(steam_data, Exception):
        print(f"[GAME-DATA] ❌ Steam erreur: {steam_data}")
        steam_data = None
    
    # 📊 ÉTAPE 2 : Scoring des résultats
    candidates = []
    
    if rawg_data and isinstance(rawg_data, dict):
        score = _score_result(game_name, rawg_data, source="RAWG", user_year=user_year)
        candidates.append((score, rawg_data, "RAWG"))
        print(f"[GAME-DATA] 📊 RAWG: {rawg_data['name']} (score: {score:.1f})")
    
    if steam_data and isinstance(steam_data, dict):
        score = _score_result(game_name, steam_data, source="Steam", user_year=user_year)
        candidates.append((score, steam_data, "Steam"))
        print(f"[GAME-DATA] 📊 Steam: {steam_data['name']} (score: {score:.1f})")
    
    # 🏆 ÉTAPE 3 : Sélectionner le meilleur
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_data, best_source = candidates[0]
        
        # Vérifier que le score est acceptable (> 50)
        if best_score >= 50:
            print(f"[GAME-DATA] 🏆 Meilleur résultat: {best_source} - {best_data['name']} (score: {best_score:.1f})")
            
            # Mettre en cache
            ttl = get_ttl_for_game(best_data.get('release_year', '?'))
            GAME_CACHE.set(cache_key, best_data, ttl=ttl)
            print(f"[GAME-DATA] 💾 Mis en cache (TTL: {ttl}s)")
            
            return best_data
        else:
            print(f"[GAME-DATA] ⚠️ Meilleur score trop faible ({best_score:.1f}), tentative IGDB...")
    
    # ⚠️ ÉTAPE 4 : Fallback IGDB API
    print("[GAME-DATA] ⚠️ RAWG + Steam échouent, tentative IGDB API...")
    
    try:
        token = get_igdb_token()
        igdb_data = query_game(game_name, token)
        
        if igdb_data:
            # Normaliser le format IGDB pour matcher RAWG
            normalized = _normalize_igdb_data(igdb_data)
            print(f"[GAME-DATA] ✅ IGDB API réussi: {normalized['name']}")
            
            # Mettre en cache aussi
            ttl = get_ttl_for_game(normalized.get('release_year', '?'))
            GAME_CACHE.set(cache_key, normalized, ttl=ttl)
            print(f"[GAME-DATA] 💾 Mis en cache (TTL: {ttl}s)")
            
            return normalized
            
    except Exception as e:
        print(f"[GAME-DATA] ❌ IGDB API erreur: {e}")
    
    # 💀 ÉTAPE 4 : Dernier recours - Web scraping IGDB
    print("[GAME-DATA] ⚠️ IGDB API échec, tentative web scraping...")
    
    try:
        web_data = await search_igdb_web(game_name)
        
        if web_data:
            # Normaliser le format web scraping
            normalized = _normalize_igdb_data(web_data)
            print(f"[GAME-DATA] ✅ Web scraping réussi: {normalized['name']}")
            
            # Mettre en cache aussi (TTL plus court car moins fiable)
            GAME_CACHE.set(cache_key, normalized, ttl=1800)  # 30min
            print(f"[GAME-DATA] 💾 Mis en cache (TTL: 1800s)")
            
            return normalized
            
    except Exception as e:
        print(f"[GAME-DATA] ❌ Web scraping erreur: {e}")
    
    # ❌ Aucune source n'a trouvé le jeu
    print(f"[GAME-DATA] ❌ Aucune source n'a trouvé '{game_name}'")
    return None


def _extract_year_from_query(query: str) -> Optional[int]:
    """
    Extrait une année de la requête utilisateur.
    Gère les formats: "2077", "2", "II", "V", etc.
    
    Args:
        query: Requête de recherche (ex: "Hades 2", "Cyberpunk 2077", "GTA V")
    
    Returns:
        Année extraite (ex: 2077, 2, 5) ou None
    """
    import re
    
    # Pattern 1: Année complète 4 chiffres (1900-2099)
    full_year_match = re.search(r'\b(19|20)\d{2}\b', query)
    if full_year_match:
        return int(full_year_match.group(0))
    
    # Pattern 2: Chiffre simple 2-9 (ex: "Hades 2" → 2)
    simple_number_match = re.search(r'\b([2-9])\b', query)
    if simple_number_match:
        return int(simple_number_match.group(0))
    
    # Pattern 3: Chiffres romains
    roman_map = {'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
    roman_match = re.search(r'\b(II|III|IV|V|VI|VII|VIII|IX|X)\b', query, re.IGNORECASE)
    if roman_match:
        return roman_map.get(roman_match.group(0).upper())
    
    return None


def _score_result(query: str, game_data: dict, source: str, user_year: Optional[int] = None) -> float:
    """
    Score un résultat final (RAWG ou Steam) avec système unifié 0-100 pts.
    
    Note: RAWG a déjà scoré ses candidats en interne, donc ici on score
    seulement le meilleur candidat retourné de chaque source pour comparaison.
    
    Scoring:
        ✅ Similarité nom: 0-50 pts
        ✅ Qualité rating: +15 pts
        ✅ Metacritic: +10 pts
        ✅ Popularité: +10 pts
        ✅ Bonus Steam indie: +5 pts
        ✅ Bonus année: +20 pts
    
    Args:
        query: Requête de recherche originale
        game_data: Données du jeu normalisées
        source: Source du résultat ("RAWG" ou "Steam")
        user_year: Année extraite de la requête (optionnel)
    
    Returns:
        Score de pertinence (0-100)
    """
    from difflib import SequenceMatcher
    
    score = 0.0
    game_name = game_data.get('name', '').lower()
    query_lower = query.lower()
    
    # 1️⃣ Similarité du nom (50 pts max)
    similarity = SequenceMatcher(None, query_lower, game_name).ratio()
    score += similarity * 50
    
    # 2️⃣ Qualité rating (15 pts)
    rating = game_data.get('rating', 0)
    if rating and rating >= 4.0:
        score += 15
    elif rating and rating >= 3.5:
        score += 8
    elif rating and rating >= 3.0:
        score += 3
    
    # 3️⃣ Metacritic (10 pts scaled)
    metacritic = game_data.get('metacritic', 0)
    if metacritic:
        score += (metacritic / 100) * 10
    
    # 4️⃣ Popularité (10 pts)
    ratings_count = game_data.get('ratings_count', 0)
    if ratings_count and ratings_count >= 1000:
        score += 10
    elif ratings_count and ratings_count >= 500:
        score += 5
    elif ratings_count and ratings_count >= 100:
        score += 2
    
    # 5️⃣ Bonus Steam indie (5 pts + devs)
    if source == "Steam":
        score += 5
        if game_data.get('developers'):
            score += 5
    
    # 6️⃣ Bonus année/suite (20 pts)
    if user_year:
        release_year = game_data.get('released')
        if release_year:
            # Extraire l'année du format "YYYY-MM-DD" ou année seule
            import re
            year_match = re.search(r'(\d{4})', str(release_year))
            if year_match:
                game_year = int(year_match.group(1))
                
                # Cas 1: Année complète (ex: "Cyberpunk 2077" → 2077)
                if user_year >= 1990 and game_year == user_year:
                    score += 20
                
                # Cas 2: Numéro de suite (ex: "Hades 2" → 2, "GTA V" → 5)
                elif user_year < 1990:
                    game_name_full = game_data.get('name', '')
                    roman_map = {2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X'}
                    
                    has_number = f" {user_year}" in game_name_full or f":{user_year}" in game_name_full
                    has_roman = roman_map.get(user_year) and f" {roman_map[user_year]}" in game_name_full
                    
                    if has_number or has_roman:
                        score += 20
    
    return score


def _normalize_igdb_data(igdb_data: dict) -> dict:
    """
    Normalise les données IGDB pour matcher le format RAWG.
    
    IGDB retourne un format différent de RAWG, cette fonction
    assure la compatibilité entre les deux sources.
    
    Args:
        igdb_data: Données brutes de IGDB
    
    Returns:
        Dict normalisé au format RAWG
    """
    # IGDB peut retourner 'release' (timestamp) ou 'first_release_date' (timestamp)
    release_ts = igdb_data.get('first_release_date') or igdb_data.get('release')
    
    # Extraire l'année depuis le timestamp
    release_year = "?"
    if release_ts:
        try:
            from datetime import datetime
            release_ts = int(release_ts)
            release_year = datetime.utcfromtimestamp(release_ts).strftime('%Y')
        except (ValueError, TypeError):
            pass
    
    # Normaliser les plateformes
    platforms = igdb_data.get('platforms', [])
    if isinstance(platforms, str):
        # Si c'est une string genre "PC, PS5, Xbox"
        platforms = [p.strip() for p in platforms.split(',')]
    elif not isinstance(platforms, list):
        platforms = []
    
    return {
        'name': igdb_data.get('name', 'Inconnu'),
        'slug': igdb_data.get('slug', ''),
        'summary': igdb_data.get('summary', 'Aucune description disponible.'),
        'release_date': release_ts,
        'release_year': release_year,
        'platforms': platforms,
        'first_release_date': release_ts,  # Garde aussi le format IGDB pour compatibilité
        # Champs RAWG absents dans IGDB
        'metacritic': None,
        'rating': None,
        'ratings_count': 0,
        'genres': [],
        'tags': [],
        'stores': [],
        'background_image': None,
    }

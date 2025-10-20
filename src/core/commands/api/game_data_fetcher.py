"""
Game Data Fetcher - Gestionnaire centralisé des sources de données de jeux.

Ce module orchestre les différentes APIs pour récupérer les informations
sur les jeux vidéo avec un système de priorité et fallback.

Priorité des sources :
    1. Cache (si disponible)
    2. RAWG (source principale - la plus complète et à jour)
    3. IGDB API (fallback si RAWG échoue)
    4. IGDB Web scraping (dernier recours)
"""
from typing import Dict, Optional

from core.cache import GAME_CACHE, get_cache_key, get_ttl_for_game

from .igdb_api import get_igdb_token, query_game, search_igdb_web
from .rawg_api import fetch_game_from_rawg


async def fetch_game_data(game_name: str, config: dict, cache_only: bool = False) -> Optional[Dict]:
    """
    Point d'entrée UNIQUE pour récupérer des données de jeu.
    
    Implémente une stratégie de fallback en cascade :
        Cache → RAWG → IGDB API → IGDB Web → None
    
    Args:
        game_name: Nom du jeu à rechercher
        config: Configuration globale du bot
        cache_only: Si True, retourne uniquement depuis le cache (tests)
    
    Returns:
        Dict avec les données du jeu (format normalisé), ou None si non trouvé.
        
        Format retourné (normalisé entre toutes les sources):
        {
            'name': str,
            'slug': str,
            'summary': str,
            'release_date': str | int,
            'release_year': str,
            'platforms': list[str] | str,
            'developers': list[str],       # Seulement si RAWG
            'publishers': list[str],       # Seulement si RAWG
            'metacritic': int | None,      # Seulement si RAWG
            'rating': float | None,        # Seulement si RAWG
            'ratings_count': int,          # Seulement si RAWG
            'genres': list[str],           # Seulement si RAWG
            'tags': list[str],             # Seulement si RAWG
            'stores': list[dict],          # Seulement si RAWG
            'background_image': str | None,# Seulement si RAWG
        }
    
    Example:
        >>> config = load_config()
        >>> data = await fetch_game_data("Hades", config)
        >>> print(f"{data['name']} - {data['rating']}/5")
        'Hades - 4.4/5'
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
        print(f"[GAME-DATA] ⚠️ Mode CACHE ONLY: Jeu non trouvé dans le cache")
        return None
    
    # � ÉTAPE 1 : RAWG en priorité (source principale)
    print("[GAME-DATA] 📡 Tentative RAWG...")
    rawg_data = await fetch_game_from_rawg(game_name, config)
    
    if rawg_data:
        print(f"[GAME-DATA] ✅ RAWG réussi: {rawg_data['name']}")
        
        # Mettre en cache avec TTL adapté
        ttl = get_ttl_for_game(rawg_data.get('release_year', '?'))
        GAME_CACHE.set(cache_key, rawg_data, ttl=ttl)
        print(f"[GAME-DATA] 💾 Mis en cache (TTL: {ttl}s)")
        
        return rawg_data
    
    # ⚠️ ÉTAPE 2 : Fallback IGDB API
    print("[GAME-DATA] ⚠️ RAWG échec, tentative IGDB API...")
    
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
    
    # 💀 ÉTAPE 3 : Dernier recours - Web scraping IGDB
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

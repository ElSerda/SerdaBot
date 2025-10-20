"""
RAWG API - Source principale pour les données de jeux vidéo.

API Documentation: https://rawg.io/apidocs
Rate limit: 1000 requêtes/jour (gratuit)
"""

from typing import Dict, List, Optional

import httpx


async def fetch_game_from_rawg(game_name: str, config: dict) -> Optional[Dict]:
    """
    Récupère les données complètes d'un jeu depuis RAWG (async).
    
    Args:
        game_name: Nom du jeu à rechercher
        config: Configuration globale du bot (contient rawg.api_key)
    
    Returns:
        Dict normalisé avec toutes les données du jeu, ou None si non trouvé.
        
        Format retourné:
        {
            'name': str,                    # Nom du jeu
            'slug': str,                    # Slug URL
            'summary': str,                 # Description complète
            'release_date': str,            # Date ISO (YYYY-MM-DD)
            'release_year': str,            # Année extraite
            'platforms': list[str],         # ['PC', 'PS5', 'Xbox']
            'developers': list[str],        # ['Supergiant Games']
            'publishers': list[str],        # ['Supergiant Games']
            'metacritic': int | None,       # Score Metacritic (0-100)
            'rating': float | None,         # Note utilisateurs (0-5)
            'ratings_count': int,           # Nombre d'avis
            'genres': list[str],            # ['Action', 'RPG']
            'tags': list[str],              # ['Open World', 'Singleplayer']
            'stores': list[dict],           # [{'name': 'Steam', 'url': '...'}]
            'background_image': str | None, # URL de l'image principale
        }
    
    Example:
        >>> config = {'rawg': {'api_key': 'xxx'}, 'bot': {'user_agent': 'SerdaBot'}}
        >>> data = await fetch_game_from_rawg("Hades", config)
        >>> print(data['name'])
        'Hades'
    """
    api_key = config.get('rawg', {}).get('api_key', '')
    if not api_key:
        print("[RAWG-API] ⚠️ Aucune clé API RAWG configurée")
        return None
    
    url = 'https://api.rawg.io/api/games'
    user_agent = config.get('bot', {}).get('user_agent', 'SerdaBot/1.0 (Twitch)')
    
    params = {
        'search': game_name,
        'page_size': 1,
        'key': api_key,
    }
    
    headers = {
        'User-Agent': user_agent,
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                print(f"[RAWG-API] ❌ Aucun résultat pour '{game_name}'")
                return None
            
            game = results[0]
            game_id = game.get('id')
            
            # Extraction et normalisation des données de base
            normalized = {
                'name': game.get('name', 'Inconnu'),
                'slug': game.get('slug', ''),
                'summary': _extract_summary(game),
                'release_date': game.get('released', ''),
                'release_year': _extract_year(game.get('released')),
                'platforms': _parse_platforms(game.get('platforms', [])),
                'developers': [],  # Sera rempli par fetch détails
                'publishers': [],  # Sera rempli par fetch détails
                'metacritic': game.get('metacritic'),
                'rating': game.get('rating'),
                'ratings_count': game.get('ratings_count', 0),
                'genres': _parse_genres(game.get('genres', [])),
                'tags': _parse_tags(game.get('tags', [])),
                'stores': _parse_stores(game.get('stores', [])),
                'background_image': game.get('background_image'),
            }
            
            # Récupérer developers/publishers depuis l'endpoint détails
            if game_id:
                details = await _fetch_game_details(game_id, api_key, user_agent)
                if details:
                    normalized['developers'] = _parse_companies(details.get('developers', []))
                    normalized['publishers'] = _parse_companies(details.get('publishers', []))
                    # Mettre à jour summary si disponible
                    if details.get('description_raw'):
                        normalized['summary'] = details['description_raw']
            
            print(f"[RAWG-API] ✅ Jeu trouvé: {normalized['name']} ({normalized['release_year']})")
            print(f"[RAWG-API] 📊 Metacritic: {normalized['metacritic']}, Rating: {normalized['rating']}/5")
            
            return normalized
            
    except httpx.TimeoutException:
        print(f"[RAWG-API] ⏱️ Timeout lors de la recherche de '{game_name}'")
        return None
    except httpx.HTTPStatusError as e:
        print(f"[RAWG-API] ❌ Erreur HTTP {e.response.status_code}: {e}")
        return None
    except Exception as e:
        print(f"[RAWG-API] ❌ Erreur inattendue: {e}")
        return None


def _extract_summary(game: dict) -> str:
    """
    Extrait la meilleure description disponible.
    Priorité: description_raw > description > slug
    """
    # Pas de description_raw dans le endpoint /games search, 
    # il faut appeler /games/{id} pour l'avoir
    # On va se contenter du slug pour l'instant
    # TODO: Faire un 2ème appel pour récupérer description_raw si besoin
    return game.get('slug', 'Pas de description disponible.')


def _extract_year(date_str: Optional[str]) -> str:
    """Extrait l'année depuis une date ISO (YYYY-MM-DD)."""
    if not date_str:
        return "?"
    try:
        return date_str.split('-')[0]
    except (IndexError, AttributeError):
        return "?"


def _parse_platforms(platforms: List[dict]) -> List[str]:
    """
    Parse la liste des plateformes depuis RAWG.
    
    Format RAWG: [{'platform': {'id': 4, 'name': 'PC', 'slug': 'pc'}}, ...]
    """
    if not platforms:
        return []
    
    platform_names = []
    for p in platforms:
        if isinstance(p, dict) and 'platform' in p:
            platform = p['platform']
            if isinstance(platform, dict):
                name = platform.get('name', '')
                if name:
                    platform_names.append(name)
    
    return platform_names


def _parse_companies(companies: List[dict]) -> List[str]:
    """
    Parse la liste des developers/publishers.
    
    Format RAWG: [{'id': 123, 'name': 'Supergiant Games', 'slug': '...'}, ...]
    """
    if not companies:
        return []
    
    return [c.get('name', '') for c in companies if isinstance(c, dict) and c.get('name')]


def _parse_genres(genres: List[dict]) -> List[str]:
    """
    Parse la liste des genres.
    
    Format RAWG: [{'id': 4, 'name': 'Action', 'slug': 'action'}, ...]
    """
    if not genres:
        return []
    
    return [g.get('name', '') for g in genres if isinstance(g, dict) and g.get('name')]


def _parse_tags(tags: List[dict]) -> List[str]:
    """
    Parse les tags principaux (limite à 5 pour éviter la surcharge).
    
    Format RAWG: [{'id': 31, 'name': 'Singleplayer', 'slug': 'singleplayer', ...}, ...]
    """
    if not tags:
        return []
    
    # Prendre les 5 premiers tags uniquement
    tag_names = [t.get('name', '') for t in tags[:5] if isinstance(t, dict) and t.get('name')]
    return tag_names


def _parse_stores(stores: List[dict]) -> List[Dict[str, str]]:
    """
    Parse la liste des stores/boutiques.
    
    Format RAWG: [{'id': 123, 'store': {'id': 1, 'name': 'Steam', ...}}, ...]
    """
    if not stores:
        return []
    
    store_list = []
    for s in stores:
        if isinstance(s, dict) and 'store' in s:
            store = s['store']
            if isinstance(store, dict):
                name = store.get('name', '')
                if name:
                    store_list.append({
                        'name': name,
                        'slug': store.get('slug', ''),
                    })
    
    return store_list


async def _fetch_game_details(game_id: int, api_key: str, user_agent: str) -> Optional[dict]:
    """
    Récupère les détails complets d'un jeu (developers, publishers, description).
    
    Endpoint: /games/{id}
    Fournit des infos supplémentaires non disponibles dans /games search.
    """
    url = f'https://api.rawg.io/api/games/{game_id}'
    params = {'key': api_key}
    headers = {'User-Agent': user_agent}
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
            
    except Exception as e:
        print(f"[RAWG-API] ⚠️ Erreur récupération détails: {e}")
        return None


async def fetch_game_details_from_rawg(game_id: int, config: dict) -> Optional[str]:
    """
    Récupère la description détaillée d'un jeu via son ID RAWG.
    
    Cette fonction fait un appel supplémentaire à /games/{id} pour obtenir
    la description complète (description_raw) qui n'est pas dans /games search.
    
    Args:
        game_id: ID RAWG du jeu
        config: Configuration du bot
    
    Returns:
        Description complète (description_raw) ou None
    """
    api_key = config.get('rawg', {}).get('api_key', '')
    user_agent = config.get('bot', {}).get('user_agent', 'SerdaBot/1.0 (Twitch)')
    
    details = await _fetch_game_details(game_id, api_key, user_agent)
    return details.get('description_raw', '') if details else None

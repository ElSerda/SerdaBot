"""
Steam Store API - Source complémentaire pour jeux indie/récents.

API Documentation: https://steamapi.xpaw.me/
Rate limit: Pas de limite officielle, mais respecter fair use
"""

from typing import Dict, List, Optional

import httpx


async def fetch_game_from_steam(game_name: str) -> Optional[Dict]:
    """
    Recherche un jeu sur Steam Store et retourne ses données normalisées.
    
    Args:
        game_name: Nom du jeu à rechercher
    
    Returns:
        Dict normalisé compatible avec format RAWG, ou None si non trouvé.
        
        Format retourné (compatible RAWG):
        {
            'name': str,
            'slug': str,
            'summary': str,
            'release_date': str,
            'release_year': str,
            'platforms': list[str],
            'developers': list[str],
            'publishers': list[str],
            'metacritic': int | None,
            'rating': float | None,
            'ratings_count': int,
            'genres': list[str],
            'tags': list[str],
            'stores': list[dict],
            'background_image': str | None,
            'steam_appid': int,  # Champ spécifique Steam
        }
    
    Example:
        >>> data = await fetch_game_from_steam("Alabaster Dawn")
        >>> print(data['name'])
        'Alabaster Dawn'
    """
    try:
        # 1. Recherche Steam Store
        search_url = 'https://store.steampowered.com/api/storesearch/'
        search_params = {
            'term': game_name,
            'l': 'french',
            'cc': 'FR',
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            search_response = await client.get(search_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            if not search_data.get('items'):
                print(f"[STEAM-API] ❌ Aucun résultat pour '{game_name}'")
                return None
            
            # Prendre le premier résultat (meilleur match Steam)
            first_result = search_data['items'][0]
            app_id = first_result['id']
            
            print(f"[STEAM-API] 🔍 Trouvé: {first_result['name']} (AppID: {app_id})")
            
            # 2. Récupérer détails complets
            details_url = 'https://store.steampowered.com/api/appdetails'
            details_params = {
                'appids': app_id,
                'l': 'french',
            }
            
            details_response = await client.get(details_url, params=details_params)
            details_response.raise_for_status()
            details_data = details_response.json()
            
            if str(app_id) not in details_data or not details_data[str(app_id)]['success']:
                print(f"[STEAM-API] ❌ Impossible de récupérer les détails pour AppID {app_id}")
                return None
            
            game = details_data[str(app_id)]['data']
            
            # 3. Normalisation au format RAWG
            normalized = {
                'name': game.get('name', 'Inconnu'),
                'slug': game.get('name', '').lower().replace(' ', '-'),
                'summary': game.get('short_description', game.get('detailed_description', '')),
                'release_date': _parse_release_date(game.get('release_date', {})),
                'released': _parse_release_date(game.get('release_date', {})),  # Compatibilité RAWG
                'release_year': _extract_year_from_steam(game.get('release_date', {})),
                'platforms': _parse_steam_platforms(game.get('platforms', {})),
                'developers': game.get('developers', []),
                'publishers': game.get('publishers', []),
                'metacritic': game.get('metacritic', {}).get('score'),
                'rating': None,  # Steam n'a pas de rating 0-5, on pourrait calculer depuis reviews
                'ratings_count': 0,  # Steam reviews nécessitent un autre endpoint
                'genres': [g.get('description', '') for g in game.get('genres', [])],
                'tags': [],  # Steam tags nécessitent parsing HTML
                'stores': [{'name': 'Steam', 'slug': 'steam'}],
                'background_image': game.get('header_image'),
                'steam_appid': app_id,
            }
            
            print(f"[STEAM-API] ✅ Jeu trouvé: {normalized['name']} ({normalized['release_year']})")
            print(f"[STEAM-API] 📊 Développeur: {', '.join(normalized['developers'][:2])}")
            
            return normalized
            
    except httpx.TimeoutException:
        print(f"[STEAM-API] ⏱️ Timeout lors de la recherche de '{game_name}'")
        return None
    except httpx.HTTPStatusError as e:
        print(f"[STEAM-API] ❌ Erreur HTTP {e.response.status_code}: {e}")
        return None
    except Exception as e:
        print(f"[STEAM-API] ❌ Erreur inattendue: {e}")
        return None


def _parse_release_date(release_info: dict) -> str:
    """
    Parse la date de sortie Steam.
    
    Format Steam: {'coming_soon': False, 'date': '25 oct. 2024'}
    Retour: ISO format 'YYYY-MM-DD' ou date string
    """
    if not release_info:
        return ""
    
    if release_info.get('coming_soon'):
        return "TBA"
    
    return release_info.get('date', '')


def _extract_year_from_steam(release_info: dict) -> str:
    """Extrait l'année depuis release_date Steam."""
    date_str = release_info.get('date', '')
    
    if not date_str or date_str == 'TBA':
        return "?"
    
    # Format Steam: "25 oct. 2024" ou "October 25, 2024"
    try:
        # Chercher un pattern d'année (4 chiffres)
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            return year_match.group(0)
    except Exception:
        pass
    
    return "?"


def _parse_steam_platforms(platforms: dict) -> List[str]:
    """
    Parse les plateformes Steam.
    
    Format Steam: {'windows': True, 'mac': False, 'linux': True}
    Retour: ['PC', 'Linux']
    """
    platform_list = []
    
    if platforms.get('windows'):
        platform_list.append('PC')
    if platforms.get('mac'):
        platform_list.append('macOS')
    if platforms.get('linux'):
        platform_list.append('Linux')
    
    return platform_list

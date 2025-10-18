import re
import time
from datetime import datetime

import httpx

from config.config import load_config

TOKEN_URL = 'https://id.twitch.tv/oauth2/token'
API_URL = 'https://api.igdb.com/v4/games'


def _get_config():
    """Charge la config de manière lazy (à la demande)."""
    return load_config()


def get_igdb_token():
    """
    Récupère un token OAuth2 valide pour IGDB (via config.yaml)
    """
    config = _get_config()
    payload = {
        'client_id': config['igdb']['client_id'],
        'client_secret': config['igdb']['client_secret'],
        'grant_type': 'client_credentials',
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = httpx.post(TOKEN_URL, data=payload, headers=headers, timeout=10)
    res.raise_for_status()
    return res.json()['access_token']


def query_game(game_name, token):
    """
    Interroge l'API IGDB pour récupérer les infos sur un jeu donné.
    """
    config = _get_config()
    headers = {
        'Client-ID': config['igdb']['client_id'],
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }

    query = f'search "{game_name}"; fields name,summary,first_release_date,platforms.name; limit 1;'
    try:
        res = httpx.post(API_URL, headers=headers, content=query)
        res.raise_for_status()
        data = res.json()
        if not data:
            return None

        game = data[0]
        name = game.get('name', 'Inconnu')
        summary = game.get('summary', 'Aucune description disponible.')
        release = game.get('first_release_date', 'Date inconnue')
        platforms = (
            ', '.join(p['name'] for p in game.get('platforms', []))
            if 'platforms' in game
            else 'N/A'
        )

        return {
            'name': name,
            'summary': summary,
            'release': release,
            'platforms': platforms,
        }
    except httpx.RequestError as e:
        print(f'❌ IGDB: Requête échouée : {e}')
        return None


def query_games_multiple(game_name: str, token: str, limit: int = 10, cache_manager=None) -> list:
    """
    Interroge l'API IGDB pour récupérer PLUSIEURS jeux matchant le nom.
    Retourne liste de dicts: {id, name, year, platforms, summary}
    
    Args:
        game_name: Nom du jeu à chercher
        token: Token IGDB OAuth2
        limit: Nombre max de résultats (défaut 10)
        cache_manager: Instance de ConversationManager pour cache L1
    
    Returns:
        Liste de jeux (0 à limit résultats)
    """
    # Check cache L1 si fourni
    if cache_manager:
        cache_key = (game_name.lower(), limit)
        cached = cache_manager.cache_get(cache_key)
        if cached:
            return cached
    
    config = _get_config()
    headers = {
        'Client-ID': config['igdb']['client_id'],
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }

    query = f'search "{game_name}"; fields name,summary,first_release_date,platforms.name; limit {limit};'
    
    try:
        res = httpx.post(API_URL, headers=headers, content=query, timeout=10)
        res.raise_for_status()
        results = res.json()
        
        if not results:
            return []
        
        # Normaliser format
        games = []
        for game in results:
            release_ts = game.get('first_release_date')
            if release_ts:
                try:
                    year = datetime.utcfromtimestamp(int(release_ts)).year
                except (ValueError, TypeError):
                    year = "?"
            else:
                year = "?"
            
            platforms_list = game.get('platforms', [])
            platforms = ', '.join(p['name'] for p in platforms_list[:3]) if platforms_list else 'N/A'
            
            games.append({
                'id': game.get('id'),
                'name': game.get('name', 'Inconnu'),
                'year': year,
                'platforms': platforms,
                'summary': game.get('summary', '')[:200],  # Limité pour mémoire
                'release': game.get('first_release_date'),  # Pour compatibilité
                'first_release_date': game.get('first_release_date')
            })
        
        # Cache si manager fourni
        if cache_manager:
            cache_key = (game_name.lower(), limit)
            cache_manager.cache_set(cache_key, games, ttl=60)
        
        return games
        
    except httpx.RequestError as e:
        print(f'❌ IGDB: Requête échouée : {e}')
        return []


# 🌐 Fallback web scraping (simple)
async def search_igdb_web(name: str) -> dict | None:
    """
    Recherche un jeu sur le site IGDB et extrait les infos clés en fallback.
    """
    slug = re.sub(r'[^\w\s-]', '', name.lower()).strip().replace(' ', '-')
    url = f'https://www.igdb.com/games/{slug}'

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
            if res.status_code != 200:
                return None
            html = res.text

            summary_match = re.search(
                r'<div class="gamepage-tabs">.*?<p>(.*?)</p>', html, re.DOTALL
            )
            summary = (
                re.sub(r'<.*?>', '', summary_match.group(1)).strip()
                if summary_match
                else 'Résumé indisponible'
            )

            name_match = re.search(r'<title>(.*?)\s+\| IGDB', html)
            title = name_match.group(1).strip() if name_match else name.title()

            return {
                'name': title,
                'summary': summary,
                'release': 'Inconnue',
                'platforms': 'Inconnues',
            }

    except Exception as e:
        print(f'❌ Erreur fallback IGDB Web : {e}')
        return None

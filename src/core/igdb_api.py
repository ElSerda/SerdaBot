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


def query_games_multiple(game_name: str, token: str, limit: int = 10, cache_manager=None, main_games_only: bool = False, 
                        franchise_name: str | None = None, only_released: bool = True) -> list:
    """
    Interroge l'API IGDB pour récupérer PLUSIEURS jeux matchant le nom.
    Retourne liste de dicts: {id, name, year, platforms, summary, total_rating, popularity}
    
    Args:
        game_name: Nom du jeu à chercher
        token: Token IGDB OAuth2
        limit: Nombre max de résultats (défaut 10)
        cache_manager: Instance de ConversationManager pour cache L1
        main_games_only: Si True, filtre categories strictes (0,1,2,3,4,10) - exclut mods/remasters/ports
        franchise_name: Si fourni, filtre par franchise (ex: "Pokémon", "God of War")
        only_released: Si True, exclut les jeux pas encore sortis
    
    Returns:
        Liste de jeux (0 à limit résultats)
    """
    # Check cache L1 si fourni
    cache_key = (game_name.lower(), limit, main_games_only, franchise_name, only_released)
    if cache_manager:
        cached = cache_manager.cache_get(cache_key)
        if cached:
            return cached
    
    config = _get_config()
    headers = {
        'Client-ID': config['igdb']['client_id'],
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }

    # Construction de la requête IGDB robuste
    where_clauses = []
    
    # Filtrer les jeux sortis seulement
    if only_released:
        now_unix = int(time.time())
        where_clauses.append(f"first_release_date != null & first_release_date <= {now_unix}")
    
    # Filtrer par franchise si spécifié (très efficace pour éliminer les fakes)
    if franchise_name:
        where_clauses.append(f'franchises.name ~ *"{franchise_name}"*')
    
    # Si main_games_only ET pas de franchise, essayer category (mais souvent vide dans IGDB)
    # On préfère le post-filtrage par blacklist
    
    # Construire la requête
    fields = "id,name,first_release_date,platforms.name,summary,total_rating,popularity,follows,hypes,franchises.name"
    where_part = f" where {' & '.join(where_clauses)}" if where_clauses else ""
    sort_part = " sort total_rating desc, popularity desc, follows desc, first_release_date desc"
    
    query = f'search "{game_name}"; fields {fields};{where_part} {sort_part} limit {limit};'
    
    try:
        # Debug: afficher la requête
        print(f"[DEBUG] IGDB query: {query}")
        
        res = httpx.post(API_URL, headers=headers, content=query, timeout=20)
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
                    year = datetime.fromtimestamp(int(release_ts)).year
                except (ValueError, TypeError):
                    year = None
            else:
                year = None
            
            platforms_list = game.get('platforms', [])
            if isinstance(platforms_list, list) and platforms_list:
                platforms = [p.get('name', '') for p in platforms_list if isinstance(p, dict)]
            else:
                platforms = []
            
            franchises_list = game.get('franchises', [])
            if isinstance(franchises_list, list) and franchises_list:
                franchises = [f.get('name', '') for f in franchises_list if isinstance(f, dict)]
            else:
                franchises = []
            
            games.append({
                'id': game.get('id'),
                'name': game.get('name', 'Inconnu'),
                'year': year,
                'platforms': platforms,
                'summary': game.get('summary', '')[:200],
                'first_release_date': game.get('first_release_date'),
                'total_rating': game.get('total_rating', 0),
                'popularity': game.get('popularity', 0),
                'follows': game.get('follows', 0),
                'hypes': game.get('hypes', 0),
                'franchises': franchises
            })
        
        # Cache si manager fourni
        if cache_manager:
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

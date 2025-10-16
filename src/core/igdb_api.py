import re

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


# 🌐 Fallback web scraping (simple)
async def search_igdb_web(name: str, config: dict) -> dict | None:
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

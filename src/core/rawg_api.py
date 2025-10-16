import requests


def query_rawg_game(game_name, config):
    api_key = config.get('rawg', {}).get('api_key', '')
    url = 'https://api.rawg.io/api/games'

    params = {
        'search': game_name,
        'page_size': 1,
    }

    if api_key:
        params['key'] = api_key

    # User-Agent configurable ou par défaut générique
    user_agent = config.get('bot', {}).get('user_agent', 'TwitchBot (https://github.com/YourRepo)')
    headers = {
        'User-Agent': user_agent,
    }

    res = requests.get(url, params=params, headers=headers, timeout=10)
    res.raise_for_status()
    results = res.json().get('results')

    if not results:
        raise Exception(f'Aucun résultat trouvé dans RAWG pour: {game_name}')

    game = results[0]
    data = {
        'name': game.get('name', 'Inconnu'),
        'summary': game.get(
            'description_raw', game.get('slug', 'Pas de description disponible.')
        ),
        'release_date': game.get('released', 'Date inconnue'),
        'platforms': ', '.join(
            [p['platform']['name'] for p in game.get('platforms', [])]
        )
        or 'Non spécifiées',
    }

    return data

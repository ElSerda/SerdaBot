"""
RAWG API - Source principale pour les données de jeux vidéo.

API Documentation: https://rawg.io/apidocs
Rate limit: 1000 requêtes/jour (gratuit)
"""

from difflib import SequenceMatcher
from typing import Dict, List, Optional

import httpx


def _score_game_candidate(game: dict, query: str) -> float:
    """
    Score un candidat de jeu selon plusieurs critères de pertinence.
    
    Args:
        game: Données brutes RAWG du jeu candidat
        query: Requête de l'utilisateur (ex: "cyberpunk", "gta")
    
    Returns:
        Score total (0-100+), plus élevé = meilleur match
        
    Critères de scoring:
        - Similarité nom: 40 pts (SequenceMatcher)
        - Bonus contextuel: 20-25 pts (cyberpunk→2077, gta→v)
        - Rating 4+: 20 pts
        - Popularité 1000+: 15 pts
        - Metacritic: 10 pts (scaled)
        - Récent (2015+): 5 pts
        - Web/Browser: -30 pts (penalty)
    """
    score = 0.0
    game_name = game.get('name', '').lower()
    query_lower = query.lower()
    
    # 1. Similarité du nom (40 pts max)
    similarity = SequenceMatcher(None, query_lower, game_name).ratio()
    score += similarity * 40
    
    # 2. Bonus contextuel (20-25 pts)
    # Détecter les patterns courants: cyberpunk→2077, gta→v, zelda→breath
    contextual_keywords = {
        'cyberpunk': ['2077', '2020'],
        'gta': ['v', 'vice', 'san andreas', 'iv'],
        'zelda': ['breath', 'tears', 'ocarina'],
        'witcher': ['3', 'wild hunt'],
        'assassin': ["creed", 'odyssey', 'valhalla'],
        'red dead': ['redemption', '2'],
        'elder scrolls': ['skyrim', 'oblivion', 'morrowind'],
    }
    
    for key, keywords in contextual_keywords.items():
        if key in query_lower:
            for keyword in keywords:
                if keyword in game_name:
                    score += 25
                    break
    
    # 3. Rating utilisateur (20 pts si >= 4.0)
    rating = game.get('rating', 0)
    if rating and rating >= 4.0:
        score += 20
    elif rating and rating >= 3.5:
        score += 10
    
    # 4. Popularité (15 pts si >= 1000 ratings)
    ratings_count = game.get('ratings_count', 0)
    if ratings_count >= 1000:
        score += 15
    elif ratings_count >= 500:
        score += 8
    
    # 5. Metacritic (10 pts max, scaled)
    metacritic = game.get('metacritic')
    if metacritic:
        score += (metacritic / 100) * 10
    
    # 6. Récence (5 pts si après 2015)
    released = game.get('released', '')
    if released:
        try:
            year = int(released.split('-')[0])
            if year >= 2015:
                score += 5
        except (ValueError, IndexError):
            pass
    
    # 7. PENALTY: Web/Browser games (-30 pts)
    platforms = game.get('platforms', []) or []
    platform_names = []
    for p in platforms:
        if p and isinstance(p, dict):
            platform_data = p.get('platform', {})
            if platform_data:
                name = platform_data.get('name', '').lower()
                if name:
                    platform_names.append(name)
    
    if platform_names:
        if any('web' in name or 'browser' in name for name in platform_names):
            # Si UNIQUEMENT Web/Browser, grosse pénalité
            if all('web' in name or 'browser' in name for name in platform_names):
                score -= 30
            else:
                # Si Web + autres plateformes, pénalité réduite
                score -= 10
        
        # 8. Bonus plateformes majeures (10 pts)
        major_platforms = ['playstation', 'xbox', 'nintendo', 'pc']
        if any(major in ' '.join(platform_names) for major in major_platforms):
            score += 10
    
    # 9. Bonus jeux AAA populaires (15 pts)
    aaa_keywords = [
        'grand theft auto', 'gta v', 'gta 5',
        'cyberpunk 2077',
        'the legend of zelda', 'breath of the wild', 'tears of the kingdom',
        'the witcher 3',
        'red dead redemption',
        'elden ring',
        'god of war',
    ]
    
    if any(keyword in game_name for keyword in aaa_keywords):
        score += 15
    
    # 10. PENALTY: Fan games, clones, mobile ports (-20 pts)
    clone_keywords = ['fan', 'clone', 'mobile', 'demo', 'scratch', 'fan-made', 'fangame']
    if any(keyword in game_name for keyword in clone_keywords):
        score -= 20
    
    # 11. PENALTY: Faible crédibilité (peu d'avis) (-20 à -30 pts)
    if ratings_count < 10:
        score -= 30
    elif ratings_count < 50:
        score -= 10
    
    # 12. PENALTY: Rating 0.0 avec peu d'avis = probablement non-jouable (-25 pts)
    if rating == 0.0 and ratings_count < 5:
        score -= 25
    
    # 13. PENALTY: Jeux très anciens (<2000) sauf si recherche explicite (-15 pts)
    # Évite les vieux jeux non pertinents (ex: GTA 1997 quand on cherche "gta")
    if released:
        try:
            year = int(released.split('-')[0])
            if year < 2000:
                score -= 15
        except (ValueError, IndexError):
            pass
    
    return score


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
        'page_size': 20,  # Fetch 20 résultats pour scorer et filtrer
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
            
            # Scorer tous les candidats
            scored_results = []
            for game in results:
                score = _score_game_candidate(game, game_name)
                scored_results.append((score, game))
                
                # Debug: afficher le score de chaque candidat
                game_display = f"{game.get('name', 'N/A')} ({_extract_year(game.get('released'))})"
                platforms = game.get('platforms') or []
                platforms_str = ', '.join([p.get('platform', {}).get('name', '') for p in platforms[:3] if p])
                print(f"[RAWG-API] 📊 Score {score:.1f}: {game_display} - {platforms_str}")
            
            # Filtrer les jeux crédibles (score >= 20)
            credible_results = [(sc, g) for sc, g in scored_results if sc >= 20]
            
            if not credible_results:
                print(f"[RAWG-API] ❌ Aucun jeu crédible trouvé (tous score < 20)")
                return None
            
            # Trier par score décroissant et prendre le meilleur
            credible_results.sort(key=lambda x: x[0], reverse=True)
            best_score, game = credible_results[0]
            
            print(f"[RAWG-API] 🏆 Meilleur match (score {best_score:.1f}): {game.get('name')}")
            
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
                'tags': _parse_tags(game.get('tags', []) or []),
                'stores': _parse_stores(game.get('stores', []) or []),
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
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"[RAWG-API] ⚠️ Détails non trouvés pour ID {game_id} (404)")
            return None  # Pas d'erreur fatale, le jeu reste utilisable
        print(f"[RAWG-API] ⚠️ Erreur HTTP {e.response.status_code}: {e}")
        return None
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

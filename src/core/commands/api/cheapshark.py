"""
CheapShark API - Prix des jeux PC en temps réel.

API Documentation: https://apidocs.cheapshark.com/
Rate limit: Aucune limite (API publique gratuite)
"""
from typing import Dict, Optional

import httpx


async def fetch_game_price(game_name: str) -> Optional[Dict]:
    """
    Récupère le prix d'un jeu PC depuis CheapShark.
    
    Args:
        game_name: Nom du jeu à rechercher
    
    Returns:
        Dict avec les infos de prix, ou None si non trouvé.
        
        Format retourné:
        {
            'game_name': str,
            'price': str,           # "20,99€" ou "Gratuit"
            'normal_price': str,    # Prix normal
            'savings': str | None,  # "15%" si promo
            'store': str,           # "Steam", "Epic Games", etc.
            'url': str,            # Lien d'achat direct
        }
    
    Example:
        >>> data = await fetch_game_price("Hades")
        >>> print(f"{data['price']} sur {data['store']}")
        '20,99€ sur Steam'
    """
    url = 'https://www.cheapshark.com/api/1.0/games'
    
    params = {
        'title': game_name,
        'limit': 1,
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                print(f"[CHEAPSHARK] ❌ Aucun résultat pour '{game_name}'")
                return None
            
            game = data[0]
            
            # Extraire le meilleur deal (cheapest)
            cheapest_price = float(game.get('cheapest', 0))
            normal_price = float(game.get('normal', cheapest_price))
            
            # Calculer la réduction si applicable
            savings = None
            if normal_price > cheapest_price and normal_price > 0:
                savings_percent = ((normal_price - cheapest_price) / normal_price) * 100
                savings = f"{int(savings_percent)}%"
            
            # Formater le prix
            if cheapest_price == 0:
                price_str = "Gratuit"
            else:
                price_str = f"{cheapest_price:.2f}€"
            
            normal_price_str = f"{normal_price:.2f}€" if normal_price > 0 else price_str
            
            result = {
                'game_name': game.get('external', game_name),
                'price': price_str,
                'normal_price': normal_price_str,
                'savings': savings,
                'store': _get_store_name(game.get('cheapestDealID', '')),
                'url': f"https://www.cheapshark.com/redirect?dealID={game.get('cheapestDealID', '')}",
            }
            
            print(f"[CHEAPSHARK] ✅ Prix trouvé: {result['price']} sur {result['store']}")
            return result
            
    except httpx.TimeoutException:
        print(f"[CHEAPSHARK] ⏱️ Timeout lors de la recherche de '{game_name}'")
        return None
    except httpx.HTTPStatusError as e:
        print(f"[CHEAPSHARK] ❌ Erreur HTTP {e.response.status_code}: {e}")
        return None
    except Exception as e:
        print(f"[CHEAPSHARK] ❌ Erreur inattendue: {e}")
        return None


def _get_store_name(deal_id: str) -> str:
    """
    Récupère le nom du store depuis le dealID.
    
    Note: Version simplifiée. Pour une version complète,
    il faudrait appeler l'API /stores pour mapper les IDs.
    """
    # TODO: Implémenter le mapping complet des stores
    # Pour l'instant, on retourne un placeholder
    return "Steam"  # Par défaut, la plupart des deals sont Steam


async def fetch_stores() -> Dict[str, str]:
    """
    Récupère la liste complète des stores CheapShark.
    
    Returns:
        Dict {store_id: store_name}
        
    Example:
        >>> stores = await fetch_stores()
        >>> print(stores['1'])
        'Steam'
    """
    url = 'https://www.cheapshark.com/api/1.0/stores'
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            stores_data = response.json()
            
            # Créer un mapping store_id -> store_name
            stores = {}
            for store in stores_data:
                store_id = store.get('storeID')
                store_name = store.get('storeName')
                if store_id and store_name:
                    stores[str(store_id)] = store_name
            
            print(f"[CHEAPSHARK] ✅ {len(stores)} stores chargés")
            return stores
            
    except Exception as e:
        print(f"[CHEAPSHARK] ⚠️ Impossible de charger les stores: {e}")
        return {}

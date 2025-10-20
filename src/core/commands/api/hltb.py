"""
HowLongToBeat API - Durée de jeu estimée.

API: Non officielle, utilise la bibliothèque howlongtobeatpy
Documentation: https://github.com/ScrappyCocco/HowLongToBeat-PythonAPI
"""
from typing import Dict, Optional


async def fetch_game_playtime(game_name: str) -> Optional[Dict]:
    """
    Récupère la durée de jeu estimée depuis HowLongToBeat.
    
    Args:
        game_name: Nom du jeu à rechercher
    
    Returns:
        Dict avec les durées estimées, ou None si non trouvé.
        
        Format retourné:
        {
            'game_name': str,
            'main_story': str | None,      # "30h" - Histoire principale
            'main_extra': str | None,      # "45h" - Histoire + extras
            'completionist': str | None,   # "120h" - 100%
            'all_styles': str | None,      # "50h" - Moyenne tous styles
        }
    
    Example:
        >>> data = await fetch_game_playtime("Hades")
        >>> print(f"Histoire: {data['main_story']}, 100%: {data['completionist']}")
        'Histoire: 22h, 100%: 95h'
    """
    # TODO: Installer la bibliothèque howlongtobeatpy
    # pip install howlongtobeatpy
    
    try:
        # Import conditionnel pour éviter les erreurs si pas installé
        from howlongtobeatpy import HowLongToBeat
        
        print(f"[HLTB] 🔍 Recherche durée pour '{game_name}'...")
        
        hltb = HowLongToBeat()
        results = await hltb.async_search(game_name)
        
        if not results:
            print(f"[HLTB] ❌ Aucun résultat pour '{game_name}'")
            return None
        
        # Prendre le premier résultat (meilleur match)
        game = results[0]
        
        result = {
            'game_name': game.game_name,
            'main_story': _format_hours(game.main_story),
            'main_extra': _format_hours(game.main_extra),
            'completionist': _format_hours(game.completionist),
            'all_styles': _format_hours(game.all_styles),
        }
        
        print(f"[HLTB] ✅ Durée trouvée: {result['main_story']} (histoire)")
        return result
        
    except ImportError:
        print("[HLTB] ⚠️ Bibliothèque howlongtobeatpy non installée")
        print("[HLTB] 💡 Installer avec: pip install howlongtobeatpy")
        return None
    except Exception as e:
        print(f"[HLTB] ❌ Erreur: {e}")
        return None


def _format_hours(hours: float | None) -> str | None:
    """
    Formate les heures en string lisible.
    
    Args:
        hours: Nombre d'heures (peut être None ou 0)
    
    Returns:
        String formatée ("30h") ou None
    """
    if not hours or hours <= 0:
        return None
    
    # Arrondir à l'heure près
    hours_int = int(round(hours))
    
    if hours_int < 1:
        return "< 1h"
    
    return f"{hours_int}h"


async def format_playtime_message(data: Dict) -> str:
    """
    Formate les données de durée en message concis.
    
    Args:
        data: Dict retourné par fetch_game_playtime()
    
    Returns:
        Message formaté pour Twitch
        
    Example:
        >>> msg = await format_playtime_message(data)
        '⏱️ Hades: 22h (histoire) | 45h (100%)'
    """
    game_name = data.get('game_name', 'Jeu')
    parts = []
    
    # Histoire principale
    if data.get('main_story'):
        parts.append(f"{data['main_story']} (histoire)")
    
    # 100%
    if data.get('completionist'):
        parts.append(f"{data['completionist']} (100%)")
    
    # Si aucune donnée
    if not parts:
        return f"⏱️ {game_name}: Durée inconnue"
    
    return f"⏱️ {game_name}: {' | '.join(parts)}"

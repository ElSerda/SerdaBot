"""
API Module - Gestion des sources de données de jeux.

Ce module centralise toutes les APIs externes pour la récupération
d'informations sur les jeux vidéo.

APIs disponibles :
    • RAWG - Informations générales (source principale)
    • IGDB - Fallback pour infos générales
    • CheapShark - Prix des jeux PC
    • HowLongToBeat - Durée de jeu estimée
"""
from .cheapshark import fetch_game_price, fetch_stores
from .game_data_fetcher import fetch_game_data
from .hltb import fetch_game_playtime, format_playtime_message
from .rawg_api import fetch_game_from_rawg

__all__ = [
    # Core
    'fetch_game_data',              # Point d'entrée principal (!gameinfo)
    'fetch_game_from_rawg',         # Accès direct RAWG
    # Prix
    'fetch_game_price',             # CheapShark (!prix)
    'fetch_stores',                 # Liste des stores
    # Durée
    'fetch_game_playtime',          # HowLongToBeat (!temps)
    'format_playtime_message',      # Formatage message durée
]

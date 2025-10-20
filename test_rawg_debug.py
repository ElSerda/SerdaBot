#!/usr/bin/env python3
"""Debug RAWG - Voir la réponse complète"""
import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import load_config
import httpx


async def debug_rawg():
    """Voir la réponse brute de RAWG."""
    config = load_config()
    api_key = config.get('rawg', {}).get('api_key', '')
    
    url = 'https://api.rawg.io/api/games'
    params = {
        'search': 'Hades',
        'page_size': 1,
        'key': api_key,
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        game = data['results'][0]
        
        print("="*60)
        print("🔍 Réponse RAWG pour Hades")
        print("="*60)
        print(json.dumps(game, indent=2))


if __name__ == "__main__":
    asyncio.run(debug_rawg())

"""
Module de gestion de l'AutoMod Twitch natif.

Permet de gérer les blocked_terms (mots bannis) et les paramètres AutoMod
directement via l'API Twitch, sans passer par le dashboard.
"""

import aiohttp
from typing import List, Dict, Optional


class TwitchAutoMod:
    """Gestion de l'AutoMod Twitch via l'API Helix.
    
    Nécessite les scopes OAuth :
    - moderator:manage:blocked_terms
    - moderator:read:blocked_terms
    - moderator:manage:automod_settings (optionnel)
    """

    def __init__(self, client_id: str, access_token: str, broadcaster_id: str, moderator_id: str):
        """
        Initialise le gestionnaire AutoMod.
        
        Args:
            client_id: Client ID de l'application Twitch
            access_token: Token OAuth avec les scopes nécessaires
            broadcaster_id: ID numérique du broadcaster (propriétaire du canal)
            moderator_id: ID numérique du bot/modérateur (généralement = bot_id)
        """
        self.client_id = client_id
        self.access_token = access_token
        self.broadcaster_id = broadcaster_id
        self.moderator_id = moderator_id
        self.base_url = "https://api.twitch.tv/helix"
        self.headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    async def add_blocked_term(self, text: str) -> Optional[Dict]:
        """
        Ajoute un mot/phrase à la liste des blocked_terms Twitch.
        
        Args:
            text: Le mot ou phrase à bloquer
            
        Returns:
            Dict avec les infos du term ajouté, ou None si erreur
        """
        url = f"{self.base_url}/moderation/blocked_terms"
        data = {
            "broadcaster_id": self.broadcaster_id,
            "moderator_id": self.moderator_id,
            "text": text
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        term_data = result.get("data", [{}])[0]
                        print(f"[AUTOMOD] ✅ Mot '{text}' ajouté avec succès (ID: {term_data.get('id', 'N/A')})")
                        return term_data
                    else:
                        error_text = await resp.text()
                        print(f"[AUTOMOD] ❌ Erreur API add_blocked_term ({resp.status}): {error_text}")
                        return None
        except Exception as e:
            print(f"[AUTOMOD] ❌ Exception add_blocked_term: {e}")
            return None

    async def remove_blocked_term(self, term_id: str) -> bool:
        """
        Retire un mot de la liste des blocked_terms.
        
        Args:
            term_id: L'ID du term à retirer (UUID retourné par l'API)
            
        Returns:
            True si succès, False sinon
        """
        url = f"{self.base_url}/moderation/blocked_terms"
        params = {
            "broadcaster_id": self.broadcaster_id,
            "moderator_id": self.moderator_id,
            "id": term_id
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=self.headers, params=params) as resp:
                    if resp.status == 204:
                        print(f"[AUTOMOD] ✅ Mot retiré avec succès (ID: {term_id})")
                        return True
                    else:
                        error_text = await resp.text()
                        print(f"[AUTOMOD] ❌ Erreur API remove_blocked_term ({resp.status}): {error_text}")
                        return False
        except Exception as e:
            print(f"[AUTOMOD] ❌ Exception remove_blocked_term: {e}")
            return False

    async def get_blocked_terms(self) -> List[Dict]:
        """
        Récupère tous les mots bannis.
        
        Returns:
            Liste de dict avec {id, text, created_at, updated_at, expires_at}
        """
        url = f"{self.base_url}/moderation/blocked_terms"
        params = {
            "broadcaster_id": self.broadcaster_id,
            "moderator_id": self.moderator_id,
            "first": 100  # Max 100 par page
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        terms = result.get("data", [])
                        print(f"[AUTOMOD] ✅ Récupéré {len(terms)} mot(s) banni(s)")
                        return terms
                    else:
                        error_text = await resp.text()
                        print(f"[AUTOMOD] ❌ Erreur API get_blocked_terms ({resp.status}): {error_text}")
                        return []
        except Exception as e:
            print(f"[AUTOMOD] ❌ Exception get_blocked_terms: {e}")
            return []

    async def find_blocked_term_by_text(self, text: str) -> Optional[Dict]:
        """
        Trouve un blocked_term par son texte.
        
        Args:
            text: Le texte à rechercher
            
        Returns:
            Le dict du term trouvé, ou None
        """
        terms = await self.get_blocked_terms()
        text_lower = text.lower()
        for term in terms:
            if term.get("text", "").lower() == text_lower:
                return term
        return None

    async def set_automod_level(self, level: int) -> bool:
        """
        Configure le niveau AutoMod global (0-4).
        
        Args:
            level: 0 (désactivé) à 4 (très strict)
            
        Returns:
            True si succès, False sinon
        """
        if not 0 <= level <= 4:
            print(f"[AUTOMOD] ❌ Niveau invalide: {level} (doit être 0-4)")
            return False

        url = f"{self.base_url}/moderation/automod_settings"
        data = {
            "broadcaster_id": self.broadcaster_id,
            "moderator_id": self.moderator_id,
            "overall_level": level
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=self.headers, json=data) as resp:
                    if resp.status == 200:
                        print(f"[AUTOMOD] ✅ Niveau AutoMod configuré: {level}")
                        return True
                    else:
                        error_text = await resp.text()
                        print(f"[AUTOMOD] ❌ Erreur API set_automod_level ({resp.status}): {error_text}")
                        return False
        except Exception as e:
            print(f"[AUTOMOD] ❌ Exception set_automod_level: {e}")
            return False

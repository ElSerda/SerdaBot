"""Module pour envoyer des messages via l'API Twitch Send Chat Message.

Ce module permet d'envoyer des messages avec le badge bot 🤖 et contourne
les restrictions de shadowban en utilisant l'API officielle au lieu d'IRC.

Avantages:
- Badge bot automatique
- Pas de shadowban
- Meilleurs rate limits
- Visible par tous les utilisateurs
"""

import logging
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


class TwitchAPISender:
    """Gestionnaire d'envoi de messages via l'API Twitch."""

    def __init__(
        self,
        client_id: str,
        app_access_token: str,
        bot_user_token: str,
        broadcaster_id: str,
        sender_id: str
    ):
        """Initialize le sender API.

        Args:
            client_id: Client ID de l'application Twitch
            app_access_token: App Access Token (pour le badge bot)
            bot_user_token: User Access Token du bot (user:write:chat)
            broadcaster_id: ID du broadcaster (channel)
            sender_id: ID du bot (sender)
        """
        self.client_id = client_id
        self.app_access_token = app_access_token
        self.bot_user_token = bot_user_token
        self.broadcaster_id = broadcaster_id
        self.sender_id = sender_id
        self.api_url = "https://api.twitch.tv/helix/chat/messages"
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Récupère ou crée la session aiohttp."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def send_message(self, message: str, use_badge: bool = True) -> bool:
        """Envoie un message dans le chat Twitch via l'API.

        Args:
            message: Le message à envoyer
            use_badge: Si True, utilise App Access Token (badge bot)
                      Si False, utilise User Access Token (pas de badge)

        Returns:
            bool: True si le message a été envoyé avec succès
        """
        try:
            # Choix du token selon si on veut le badge ou non
            token = self.app_access_token if use_badge else self.bot_user_token

            headers = {
                "Authorization": f"Bearer {token}",
                "Client-Id": self.client_id,
                "Content-Type": "application/json"
            }

            payload = {
                "broadcaster_id": self.broadcaster_id,
                "sender_id": self.sender_id,
                "message": message
            }

            session = await self._get_session()
            async with session.post(self.api_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("data", [{}])[0].get("is_sent"):
                        logger.debug(f"✅ Message envoyé via API: {message[:50]}...")
                        return True
                    else:
                        drop_reason = data.get("data", [{}])[0].get("drop_reason")
                        logger.warning(f"❌ Message droppé: {drop_reason}")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Erreur API ({response.status}): {error_text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Exception lors de l'envoi API: {e}")
            return False

    async def close(self):
        """Ferme proprement la session aiohttp."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

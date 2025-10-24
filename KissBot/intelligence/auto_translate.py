"""
Auto-translate Events - Devs Whitelist Integration
Gestion des messages auto-traduits pour devs whitelistés
"""

import json
import os
from datetime import datetime


class AutoTranslateHandler:
    """Gestionnaire auto-traduction devs whitelist."""
    
    def __init__(self, bot, translate_function):
        self.bot = bot
        self.translate_function = translate_function
    
    async def handle_message(self, message):
        """Traite un message pour auto-traduction si nécessaire."""
        
        # Skip messages du bot lui-même
        if message.author.name.lower() == self.bot.nick.lower():
            return
        
        # Skip commandes (commence par !)
        if message.content.startswith('!'):
            return
        
        # Check si user est dans whitelist
        if not self._is_dev_whitelisted(message.author.name):
            return
        
        # Check si auto-translate activé
        devs_data = self._load_devs_whitelist()
        if not devs_data.get('auto_translate', True):
            return
        
        # Check si message pas français
        if self._is_french_message(message.content):
            return
        
        # Check longueur minimum
        if len(message.content.strip()) < 5:
            return
        
        try:
            # Traduction
            translated = await self.translate_function(message.content)
            
            # Envoi traduction
            await message.channel.send(f"🌍 {message.author.name}: {translated}")
            
        except Exception as e:
            self.bot.logger.error(f"Erreur auto-translate: {e}")
    
    def _is_dev_whitelisted(self, username: str) -> bool:
        """Vérifie si user est dans whitelist devs."""
        devs_data = self._load_devs_whitelist()
        return username.lower() in [dev.lower() for dev in devs_data.get('devs', [])]
    
    def _load_devs_whitelist(self) -> dict:
        """Charge la whitelist des devs depuis JSON."""
        devs_file = "data/devs_whitelist.json"
        
        try:
            if os.path.exists(devs_file):
                with open(devs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.bot.logger.error(f"Erreur lecture devs whitelist: {e}")
        
        return {"devs": [], "auto_translate": True}
    
    def _is_french_message(self, text: str) -> bool:
        """Détection simple si un message est en français."""
        if not text or len(text.strip()) < 3:
            return True
        
        # Mots français communs
        french_words = {
            'le', 'la', 'de', 'et', 'à', 'un', 'une', 'du', 'des', 'les',
            'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
            'avoir', 'être', 'faire', 'aller', 'voir', 'savoir', 'pouvoir',
            'avec', 'pour', 'dans', 'sur', 'par', 'sans', 'sous', 'entre',
            'très', 'plus', 'moins', 'bien', 'mal', 'tout', 'tous', 'toutes',
            'bonjour', 'salut', 'merci', 'oui', 'non', 'peut', 'être'
        }
        
        words = set(word.lower().strip('.,!?;:()[]{}"\'-') for word in text.split()[:10])
        french_count = sum(1 for word in words if word in french_words)
        
        # Si 25%+ des mots sont français = probablement français
        return french_count >= len(words) * 0.25
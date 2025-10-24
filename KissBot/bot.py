"""
KissBot - Bot Twitch avec architecture 3-pillar
Refactorisation KISS avec Components TwitchIO
"""

import logging
import time
from typing import Dict
from twitchio.ext import commands

# Core imports
try:
    from core import RateLimiter, CacheManager
    print("✅ Core imports OK")
except Exception as e:
    print(f"❌ Core import error: {e}")
    raise

# Backend imports
try:
    from backends import game_cache
    from intelligence.auto_translate import AutoTranslateHandler
    print("✅ Backend imports OK")
except Exception as e:
    print(f"❌ Backend import error: {e}")
    raise


class KissBot(commands.Bot):
    """Bot principal TwitchIO 2.x - Architecture modulaire."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration Twitch
        twitch_config = config.get("twitch", {})
        
        # TwitchIO 2.x setup
        super().__init__(
            token=twitch_config.get("token", ""),
            prefix=twitch_config.get("prefix", "!"),
            initial_channels=twitch_config.get("channels", ["el_serda"])
        )
        
        # Core components
        self.rate_limiter = RateLimiter(default_cooldown=5.0)
        self.cache_manager = CacheManager(config)
        self.game_cache = game_cache
        
        # Stats
        self.start_time = time.time()
        
        # Charger les Components (TwitchIO 2.x - doit être dans __init__)
        # Pillar 1: Commands (pure code)
        try:
            print("🔧 Loading game_commands...")
            self.load_module('commands.game_commands')
            print("✅ game_commands loaded")
        except Exception as e:
            print(f"❌ Error loading game_commands: {e}")
            raise
        
        try:
            print("🔧 Loading translation...")
            self.load_module('commands.translation')
            print("✅ translation loaded")
        except Exception as e:
            print(f"❌ Error loading translation: {e}")
            raise
        
        try:
            print("🔧 Loading utils_commands...")
            self.load_module('commands.utils_commands')
            print("✅ utils_commands loaded")
        except Exception as e:
            print(f"❌ Error loading utils_commands: {e}")
            raise
        
        # Pillar 2: Intelligence (LLM/IA)
        try:
            print("🔧 Loading intelligence.commands...")
            self.load_module('intelligence.commands')
            print("✅ intelligence.commands loaded")
        except Exception as e:
            print(f"❌ Error loading intelligence.commands: {e}")
            raise
        
        # Pillar 3: Twitch Events (Phase 2 - EventSub)
        # À implémenter si besoin
        
        self.logger.info("🤖 KissBot V1 - 3-Pillar KISS Architecture")
        
        # Auto-translate handler setup
        self._setup_auto_translate()
    
    def _setup_auto_translate(self):
        """Setup auto-translate handler pour devs whitelist."""
        try:
            # Auto-translate désactivé par choix architectural KISS
            # La traduction manuelle !trad est suffisante pour les besoins
            self.auto_translate = None
            self.logger.info("🌍 Auto-translate désactivé (utilise !trad pour traduction manuelle)")
        except Exception as e:
            self.logger.warning(f"Auto-translate non disponible: {e}")
            self.auto_translate = None
        self.logger.info("✅ Tous les Components chargés")
    
    async def event_ready(self):
        """Event de connexion réussie."""
        bot_name = self.nick
        channels = self.config.get("twitch", {}).get("channels", ["el_serda"])
        
        self.logger.info(f"✅ Bot connecté: {bot_name}")
        self.logger.info(f"📺 Channels: {self.connected_channels}")
        self.logger.info("🎮 KissBot prêt avec architecture 3-pillar !")
        print(f"🚀 CONNEXION RÉUSSIE - Bot: {bot_name} - Channels: {channels}")
        
        # Message de bienvenue EPIC
        try:
            for channel in self.connected_channels:
                # Message de connexion avec style
                welcome_msg = (
                    f"👋 Coucou {channel.name} ! | "
                    f"👾 serda_bot V1.0 connecté ! | "
                    f"🎮 Essayez !gc pour voir le jeu actuel | "
                    f"🤖 !gameinfo <jeu> pour infos détaillées | "
                    f"💬 !ask <question> pour me parler"
                )
                await channel.send(welcome_msg)
                self.logger.info(f"💬 Message de bienvenue envoyé dans #{channel.name}")
        except Exception as e:
            self.logger.error(f"Erreur envoi bienvenue: {e}")
    
    async def event_message(self, message):
        """Traitement des messages avec auto-translate devs."""
        # Ignorer ses propres messages
        if message.echo:
            return
        
        # Log du message
        self.logger.info(f"📝 Message de {message.author.name}: {message.content}")
        print(f"📝 {message.author.name}: {message.content}")
        
        # Auto-translate devs whitelist (avant commands) - temporairement désactivé
        if hasattr(self, 'auto_translate') and self.auto_translate:
            try:
                await self.auto_translate.handle_message(message)
            except Exception as e:
                self.logger.error(f"Erreur auto-translate: {e}")
        
        # Traiter les commandes (!cmd)
        await self.handle_commands(message)
        
        # Traiter les mentions (@bot)
        bot_name = self.nick.lower()
        if bot_name in message.content.lower() or f"@{bot_name}" in message.content.lower():
            self.logger.info(f"🎯 Mention détectée ! Bot: {bot_name}, Message: {message.content}")
            await self.handle_mention(message)
    
    async def event_command_error(self, context, error):
        """Gestion des erreurs de commandes."""
        error_str = str(error).lower()
        
        # Ignorer les commandes inconnues (silencieux)
        # Check pour "was found" au lieu de "not found" (plus fiable)
        if "was found" in error_str or "command" in error_str and "found" in error_str:
            # Silencieux - pas de log, pas de message
            return
        
        # Logger les vraies erreurs
        self.logger.error(f"Erreur commande {context.command}: {error}")
        await context.send("❌ Une erreur s'est produite. Réessayez plus tard.")
    
    async def handle_mention(self, message):
        """Gère les mentions du bot (délègue à intelligence.events)."""
        self.logger.info(f"🔄 handle_mention START pour {message.author.name}")
        
        from intelligence.events import handle_mention
        
        # Rate limiting
        if not self.rate_limiter.is_allowed(message.author.name, cooldown=15.0):
            self.logger.info(f"⏱️ Rate limit actif pour {message.author.name}")
            return  # Ignorer silencieusement
        
        self.logger.info(f"✅ Rate limit OK, appel LLM...")
        
        try:
            response = await handle_mention(self, message)
            self.logger.info(f"📥 LLM Response: {response}")
            
            if response:
                await message.channel.send(response)
                self.logger.info(f"💬 Réponse envoyée")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur mention: {e}", exc_info=True)
    
    async def close(self):
        """Nettoyage à la fermeture."""
        self.logger.info("👋 KissBot arrêté proprement")
        await super().close()

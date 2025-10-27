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
    try:
        from core import QuantumCache
        QUANTUM_AVAILABLE = True
    except ImportError:
        QUANTUM_AVAILABLE = False
    print("✅ Core imports OK")
except Exception as e:
    print(f"❌ Core import error: {e}")
    raise

# Backend imports
try:
    from backends import game_cache
    if QUANTUM_AVAILABLE:
        try:
            from backends.quantum_game_cache import QuantumGameCache
            QUANTUM_GAME_AVAILABLE = True
        except ImportError:
            QUANTUM_GAME_AVAILABLE = False
    else:
        QUANTUM_GAME_AVAILABLE = False
    # Auto-translate désactivé pour KISS V1
    # from intelligence.auto_translate import AutoTranslateHandler
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
        
        # Système quantique (optionnel)
        if QUANTUM_AVAILABLE and QUANTUM_GAME_AVAILABLE:
            try:
                self.quantum_cache = QuantumCache(config)
                self.quantum_game_cache = QuantumGameCache(config)
                self.logger.info("🔬 Système quantique initialisé")
            except Exception as e:
                self.logger.warning(f"⚠️ Quantum cache désactivé: {e}")
                self.quantum_cache = None
                self.quantum_game_cache = None
        else:
            self.quantum_cache = None
            self.quantum_game_cache = None
        
        # Stats
        self.start_time = time.time()
        
        # 🔬 QUANTUM PIPELINE PHILOSOPHY
        # États en superposition jusqu'à observation utilisateur
        self.quantum_pipeline = {
            'user_states': {},  # États des utilisateurs en superposition
            'command_superpositions': {},  # Commandes en états multiples
            'observation_history': [],  # Historique des observations
            'entangled_users': []  # Utilisateurs intriqués
        }
        
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
        
        # Commandes quantiques (optionnelles)
        try:
            print("🔧 Loading quantum_game_commands...")
            self.load_module('commands.quantum_game_commands')
            print("✅ quantum_game_commands loaded")
        except Exception as e:
            print(f"⚠️ Quantum commands non disponibles: {e}")
        
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
        # Auto-translate désactivé pour architecture KISS V1
        self.logger.info("🌍 Auto-translate désactivé (utilise !trad pour traduction manuelle)")
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
                self.logger.info(f"💬 Message de bienvenue envoyé dans {channel.name}") #{channel.name}")
        except Exception as e:
            self.logger.error(f"Erreur envoi bienvenue: {e}")
    
    async def event_message(self, message):
        """Traitement quantique des messages avec superposition d'états."""
        # Ignorer ses propres messages
        if message.echo:
            return
        
        # 🔬 QUANTUM OBSERVATION: Chaque message observe l'état de l'utilisateur
        await self.quantum_observe_user(message.author.name, message.content)
        
        # Log du message
        self.logger.info(f"📝 Message de {message.author.name}: {message.content}")
        print(f"📝 {message.author.name}: {message.content}")
        
        # Auto-translate désactivé pour KISS V1
        # La traduction manuelle !trad est suffisante
        
        # 🔬 QUANTUM COMMAND PROCESSING: Superposition avant collapse
        await self.handle_quantum_commands(message)
        
        # Traiter les mentions (@bot) avec intrication quantique
        bot_name = self.nick.lower()
        if bot_name in message.content.lower() or f"@{bot_name}" in message.content.lower():
            self.logger.info(f"🎯 Mention quantique détectée ! Bot: {bot_name}, Message: {message.content}")
            await self.handle_quantum_mention(message)
    
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

    # 🔬⚛️ QUANTUM PIPELINE METHODS
    # ========================================
    
    async def quantum_observe_user(self, username: str, message_content: str):
        """
        🔍 Observer quantiquement un utilisateur
        
        PHILOSOPHIE: Chaque message observe l'état de l'utilisateur
        et peut faire collapser ses états en superposition
        """
        if username not in self.quantum_pipeline['user_states']:
            # Créer superposition initiale
            self.quantum_pipeline['user_states'][username] = {
                'state': 'superposition',
                'possible_intents': ['gaming', 'chat', 'help', 'question'],
                'confidence': 0.5,
                'last_observation': message_content,
                'observation_count': 0
            }
        
        user_state = self.quantum_pipeline['user_states'][username]
        user_state['observation_count'] += 1
        user_state['last_observation'] = message_content
        
        # Analyser intent et potentiellement collapser l'état
        if message_content.startswith('!'):
            user_state['state'] = 'command_mode'
            user_state['confidence'] = 0.9
        elif '?' in message_content:
            user_state['state'] = 'question_mode'
            user_state['confidence'] = 0.8
        
        # Enregistrer observation
        self.quantum_pipeline['observation_history'].append({
            'username': username,
            'content': message_content,
            'timestamp': time.time(),
            'resulting_state': user_state['state']
        })
        
        self.logger.debug(f"🔬 Observation quantique: {username} → {user_state['state']}")
    
    async def handle_quantum_commands(self, message):
        """
        🎮 Traitement quantique des commandes
        
        SUPERPOSITION: Commandes existent en plusieurs états possibles
        COLLAPSE: L'exécution fixe l'état final
        """
        content = message.content.strip()
        
        if not content.startswith('!'):
            return
        
        command_key = f"cmd_{message.author.name}_{int(time.time())}"
        
        # Créer superposition de commande
        self.quantum_pipeline['command_superpositions'][command_key] = {
            'raw_command': content,
            'possible_interpretations': [],
            'execution_state': 'superposition',
            'user': message.author.name
        }
        
        # Analyser les interprétations possibles
        cmd_word = content.split()[0].lower()
        interpretations = []
        
        if 'game' in cmd_word:
            interpretations.extend(['game_search', 'game_info', 'quantum_game'])
        if 'help' in cmd_word:
            interpretations.append('help_request')
        if 'q' in cmd_word:
            interpretations.append('quantum_operation')
        
        self.quantum_pipeline['command_superpositions'][command_key]['possible_interpretations'] = interpretations
        
        # Traiter avec TwitchIO classique (collapse vers exécution)
        await self.handle_commands(message)
        
        # Marquer comme collapsed
        if command_key in self.quantum_pipeline['command_superpositions']:
            self.quantum_pipeline['command_superpositions'][command_key]['execution_state'] = 'collapsed'
    
    async def handle_quantum_mention(self, message):
        """
        🌟 Traitement quantique des mentions
        
        INTRICATION: Mention crée lien quantique bot ↔ utilisateur
        """
        username = message.author.name
        
        # Créer intrication quantique
        self.quantum_pipeline['entangled_users'].append({
            'username': username,
            'entanglement_time': time.time(),
            'message_context': message.content,
            'correlation_strength': 0.8
        })
        
        # Déléguer au handler classique avec contexte quantique
        await self.handle_mention(message)
        
        self.logger.info(f"⚛️ Intrication quantique créée avec {username}")
    
    def get_quantum_pipeline_stats(self) -> dict:
        """📊 Statistiques du pipeline quantique"""
        return {
            'total_users_observed': len(self.quantum_pipeline['user_states']),
            'active_superpositions': len([
                cmd for cmd in self.quantum_pipeline['command_superpositions'].values()
                if cmd['execution_state'] == 'superposition'
            ]),
            'total_observations': len(self.quantum_pipeline['observation_history']),
            'entangled_users': len(self.quantum_pipeline['entangled_users']),
            'quantum_enabled': self.quantum_cache is not None
        }
    
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

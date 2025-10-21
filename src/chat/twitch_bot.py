"""Module de gestion du bot Twitch SerdaBot.

Ce module implémente les fonctionnalités principales du bot Twitch, notamment :
- La gestion des commandes (!ask, !game, etc.)
- La traduction automatique des messages
- La détection et le timeout des bots spam
- La gestion des cooldowns

Le bot utilise TwitchIO comme base et ajoute des fonctionnalités personnalisées.
"""

import asyncio
import re
import sys
import traceback
from datetime import datetime, timedelta

from twitchio.ext import commands  # type: ignore

from src.config.config import load_config
from src.core.commands.ask_command import handle_ask_command
from src.core.commands.cache_commands import (
    handle_cacheadd_command,
    handle_cacheclear_command,
    handle_cachestats_command,
)
from src.core.commands.chill_command import handle_chill_command
from src.core.commands.donation_command import handle_donation_command
from src.core.commands.game_command import handle_game_command
from src.utils.cache_manager import load_cache
from src.utils.conversation_manager import ConversationManager
from src.utils.llm_detector import check_llm_status, get_llm_mode
from src.utils.translator import Translator
from src.utils.twitch_api_sender import TwitchAPISender
from src.utils.twitch_automod import TwitchAutoMod

CONFIG = load_config()


# Gestionnaire global pour capturer les exceptions non gérées
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("[ERROR] Une exception non gérée a été capturée :")
    print("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))


sys.excepthook = handle_exception


class TwitchBot(commands.Bot):  # pyright: ignore[reportPrivateImportUsage]
    """Bot Twitch personnalisé avec gestion des commandes et de la traduction automatique.

    Cette classe étend le Bot TwitchIO standard avec des fonctionnalités personnalisées
    comme la traduction automatique, la gestion du spam et diverses commandes utilitaires.
    """

    def __init__(self, config_or_path: dict | str = 'src/config/config.yaml'):
        # Support à la fois dict (déjà chargé) et string (path à charger)
        config: dict
        if isinstance(config_or_path, dict):
            config = config_or_path
        else:
            config = load_config(config_or_path)
        
        self.config: dict = config
        
        # Initialize TwitchIO Bot parent class
        super().__init__(
            token=self.config["twitch"]["token"],
            prefix='!',
            initial_channels=[self.config["bot"]["channel"]]
        )
        
        # Initialise le cache (avec reset si mode expérimental)
        reset_cache = self.config.get("bot", {}).get("reset_cache_on_boot", False)
        load_cache(reset=reset_cache)
        self.cooldowns = {}
        self.botname = self.config["bot"]["name"].lower()
        self.enabled = self.config["bot"].get("enabled_commands", [])

        # Initialize translator
        self.translator = Translator()
        self.auto_translate = self.config["bot"].get("auto_translate", True)

        # Initialize conversation manager (contexte conversationnel)
        rate_limiting = self.config.get("rate_limiting", {})
        max_idle_time = rate_limiting.get("max_idle_time", 3600)
        max_messages = rate_limiting.get("max_messages_per_user", 12)
        self.conversation_manager = ConversationManager(ttl_seconds=max_idle_time, max_messages=max_messages)
        print(f"💬 ConversationManager activé (TTL: {max_idle_time}s, max: {max_messages} messages)")

        # Initialize AutoMod (if credentials available)
        try:
            self.automod = TwitchAutoMod(
                client_id=self.config["twitch"]["client_id"],
                access_token=self.config["twitch"]["token"].replace("oauth:", ""),
                broadcaster_id=self.config["twitch"].get("broadcaster_id", self.config["twitch"]["bot_id"]),
                moderator_id=self.config["twitch"]["bot_id"]
            )
            self.automod_enabled = True
        except (KeyError, TypeError) as e:
            print(f"⚠️ AutoMod désactivé (config manquante): {e}")
            self.automod_enabled = False

        # Initialize API Sender (badge bot 🤖)
        try:
            self.api_sender = TwitchAPISender(
                client_id=self.config["twitch"]["client_id"],
                app_access_token=self.config["twitch"]["app_access_token"],
                bot_user_token=self.config["twitch"]["app_access_token"],  # On utilise l'app token
                broadcaster_id=self.config["twitch"]["broadcaster_id"],
                sender_id=self.config["twitch"]["bot_id"]
            )
            self.api_enabled = True
            print("🤖 API Send Chat Message activée (badge bot enabled)")
        except (KeyError, TypeError) as e:
            print(f"⚠️ API Send Chat désactivée (config manquante): {e}")
            self.api_enabled = False

        # Track first connection for welcome message
        self._first_connect_done = False
        
        # Reconnection tracking (TwitchIO 2.x native - Solution optimisée)
        self._booted = False
        
        # Détection du LLM au démarrage
        llm_mode = get_llm_mode(self.config)
        
        if llm_mode == "disabled":
            self.llm_available = False
            print("🔇 LLM désactivé manuellement (config ou LLM_MODE=disabled)")
        elif llm_mode == "enabled":
            self.llm_available = True
            print("🔊 LLM forcé activé (config ou LLM_MODE=enabled)")
        else:  # auto
            self.llm_available, status_msg = check_llm_status(self.config)
            print(status_msg)
            if not self.llm_available:
                print("🔄 Note: Le LLM sera revérifié à chaque appel (retry intelligent)")
        self._channel_joined_once = False  # Track première connexion vs reconnexion
        self._last_reconnect_announce = 0  # Timestamp pour cooldown anti-spam

    async def event_ready(self):
        print(f'\n🤖 Connected to Twitch chat as {self.nick}')
        self._display_model_config()
        print("☕️ Boot complete.")
        print("🤖 SerdaBot is online and ready.")
        self._booted = True

        # Envoie le message de connexion uniquement à la première connexion
        if not self._first_connect_done:
            self._first_connect_done = True
            connect_message = self.config["bot"].get("connect_message", "").strip()
            if connect_message and self.connected_channels:
                try:
                    await self.safe_send(self.connected_channels[0], connect_message)
                except Exception as e:
                    print(f"[ERROR] Impossible d'envoyer le message de connexion : {e}")

    def _display_model_config(self):
        """Affiche la configuration du modèle au démarrage."""
        try:
            print("\n🧠 === CONFIGURATION MODÈLE ===")

            # Endpoint externe (LM Studio/FastAPI)
            endpoint = self.config["bot"].get("model_endpoint") or self.config["bot"].get("api_url")
            if endpoint:
                endpoint_type = (
                    "LM Studio"
                    if "1234" in endpoint
                    else "FastAPI" if "8000" in endpoint else "Externe"
                )
                print(f"🌐 {endpoint_type}: {endpoint}")

            # OpenAI fallback
            if self.config["bot"].get("model_type") == "openai":
                model = self.config["bot"].get("openai_model", "gpt-3.5-turbo")
                print(f"🌐 Fallback: OpenAI ({model})")

            # Commandes activées
            enabled = self.config["bot"].get("enabled_commands", [])
            print(f"⚡ Commandes: {', '.join(enabled)}")
            print("=" * 35)
        except Exception as e:
            print(f"[ERROR] Une erreur s'est produite lors de l'affichage de la configuration : {e}")

    def _is_bot_mentioned(self, message, content: str, cleaned: str) -> bool:
        """Vérifie si le bot est mentionné dans le message.
        
        Détecte 3 types de mentions:
        1. Nom du bot dans le message (ex: "serdabot tu es là?")
        2. Mention @ (ex: "@serdabot bonjour")
        3. Réponse Twitch (bouton "Répondre" dans le chat)
        
        Args:
            message: L'objet message TwitchIO
            content: Le contenu brut du message
            cleaned: Le contenu nettoyé (sans caractères spéciaux)
            
        Returns:
            bool: True si le bot est mentionné
        """
        # 1. Vérifier si le nom du bot est dans le message nettoyé (méthode originale)
        words = re.findall(r"\b\w+\b", cleaned)
        if self.botname in words:
            return True
        
        # 2. Vérifier les mentions @ dans le contenu original
        # Pattern: @botname (au début ou milieu de phrase)
        mention_pattern = rf"@{re.escape(self.botname)}\b"
        if re.search(mention_pattern, content.lower()):
            return True
        
        # 3. Vérifier si c'est une réponse Twitch au bot
        # TwitchIO expose les tags IRC via message.tags
        if hasattr(message, 'tags') and message.tags:
            # Le tag 'reply-parent-user-login' contient le nom de l'utilisateur auquel on répond
            reply_parent = message.tags.get('reply-parent-user-login', '').lower()
            if reply_parent == self.botname:
                return True
        
        return False

    async def run_with_cooldown(self, user, action):
        """Execute action with cooldown management and error handling."""
        try:
            await action()
        except ValueError as e:
            print(f"❌ Erreur de valeur dans la commande de @{user} : {e}")
        except ConnectionError as e:
            print(f"❌ Erreur de connexion pour @{user} : {e}")
        except TimeoutError as e:
            print(f"❌ Délai d'attente dépassé pour @{user} : {e}")
        except asyncio.CancelledError:
            print(f"❌ Commande annulée pour @{user}")
            raise  # On re-lève cette exception car elle est importante pour asyncio
        except (RuntimeError, AttributeError, KeyError) as e:
            print(f"❌ Erreur inattendue pour @{user} : {type(e).__name__} - {e}")
            # Log l'erreur pour debug ultérieur
            print("Détails de l'erreur:")
            print(traceback.format_exc())
        finally:
            self.cooldowns[user] = datetime.now()
            print(
                f'[{datetime.now().strftime("%H:%M:%S")}] ✅ Prêt à écouter de nouvelles commandes.'
            )

    async def event_message(self, message) -> None:
        """Gère les messages reçus dans le chat.

        Cette méthode est appelée à chaque message reçu. Elle gère :
        - La détection de spam
        - La traduction automatique
        - Les commandes du bot

        Args:
            payload: Le message reçu du chat Twitch
        """
        if message.echo:
            return

        content = str(message.content).strip()
        user = str(message.author.name or "user").lower()
        now = datetime.now()
        cooldown = self.config["bot"].get("cooldown", 60)
        
        # Remove @mention from start for command parsing
        content_without_mention = re.sub(r"^@\w+\s+", "", content)
        cleaned = re.sub(r"[^\w\s!?]", "", content_without_mention.lower())
        
        # Check if bot is mentioned (nom, @mention, ou reply Twitch)
        is_mentioned = self._is_bot_mentioned(message, content, cleaned)

        # === CHECK BOT WHITELIST/BLACKLIST ===
        if self.translator.should_ignore_bot(user):
            print(f"🚫 Bot ignoré (whitelist/blacklist): {user}")
            return

        # === CHECK SI C'EST UNE COMMANDE MOD (avant spam detection) ===
        is_mod = (
            getattr(message.author, 'is_mod', False)
            or user == message.channel.name.lower()
        )

        # Si c'est un mod qui utilise une commande de gestion, on skip la détection de spam
        is_management_command = is_mod and any(
            cleaned.startswith(cmd) for cmd in [
                "!adddev", "!removedev", "!deldev", "!listdevs",
                "!blocksite", "!unblocksite", "!blockedlist",
                "!addwhitebot", "!delwhitebot", "!addblackbot", "!delblackbot",
                "!whitebots", "!blackbots", "!translate ", "!trad "
            ]
        )

        # === SPAM BOT DETECTION & BAN (sauf si commande de gestion) ===
        if not is_management_command:
            channel_owner = message.channel.name.lower()
            if self.translator.is_spam_bot(user, content, channel_owner):
                print(f"🚫 Spam bot détecté: {user} - Message: {content[:50]}")
                try:
                    # Timeout le bot spam (60s = 1min) - Via commande chat
                    timeout_command = f"/timeout {user} 60"
                    await message.channel.send(timeout_command)
                    print(f"✅ Commande timeout envoyée: {user} (60 sec)")
                except (ConnectionError, TimeoutError) as e:
                    print(f"❌ Erreur réseau lors du timeout de {user}: {e}")
                except ValueError as e:
                    print(f"❌ Erreur de valeur lors du timeout de {user}: {e}")
                except RuntimeError as e:
                    print(f"❌ Erreur d'exécution lors du timeout de {user}: {e}")
                return
            else:
                # Log pour debug (optionnel)
                print(f"💬 Message de {user}: {content[:30]}... [OK]")

        # === AUTO-TRADUCTION DEVS ===
        if self.auto_translate and self.translator.should_translate(user, content):
            try:
                translated = self.translator.translate(content, "en", "fr")
                if translated and not translated.startswith("⚠️"):
                    formatted = f"🌐 @{user}: {content}\n└─ 🇫🇷 {translated}"
                    await self.safe_send(message.channel, formatted)
                elif translated and translated.startswith("⚠️"):
                    # Erreur de traduction, mais on affiche quand même un message d'info
                    await self.safe_send(message.channel, f"🌐 @{user}: {content}\n└─ {translated}")
            except (RuntimeError, ValueError, KeyError) as e:
                print(f"❌ Erreur auto-traduction pour {user}: {e}")
                # En cas d'erreur critique, on affiche juste le message original
                await self.safe_send(
                    message.channel,
                    f"🌐 @{user}: {content}\n└─ ⚠️ Traduction indisponible"
                )

        # Check cooldown
        if user in self.cooldowns and now - self.cooldowns[user] < timedelta(seconds=cooldown):
            remaining = int(cooldown - (now - self.cooldowns[user]).total_seconds())
            print(f"⏳ {user} en cooldown ({remaining}s restant)")
            return

        # === COMMANDES TRADUCTION (MOD ONLY) ===
        if cleaned.startswith("!adddev") and is_mod:
            parts = content.split()
            if len(parts) > 1:
                username = parts[1].strip("@")
                self.translator.add_dev(username)
                await self.safe_send(
                    message.channel, f"✅ @{username} ajouté à la whitelist traduction !"
                )
            else:
                await self.safe_send(message.channel,  f"@{user} Usage: !adddev @username")
            return

        elif (cleaned.startswith("!removedev") or cleaned.startswith("!deldev")) and is_mod:
            parts = content.split()
            if len(parts) > 1:
                username = parts[1].strip("@")
                if self.translator.remove_dev(username):
                    await self.safe_send(message.channel,  f"✅ @{username} retiré de la whitelist.")
                else:
                    await self.safe_send(
                        message.channel, f"ℹ️ @{username} n'est pas dans la whitelist."
                    )
            else:
                cmd_used = "!deldev" if cleaned.startswith("!deldev") else "!removedev"
                await self.safe_send(message.channel,  f"@{user} Usage: {cmd_used} @username")
            return

        elif cleaned.startswith("!listdevs") and is_mod:
            devs = self.translator.get_devs()
            if devs:
                devs_str = ", ".join(f"@{d}" for d in devs)
                await self.safe_send(
                    message.channel, f"📋 Devs whitelistés ({len(devs)}): {devs_str}"
                )
            else:
                await self.safe_send(message.channel,  "ℹ️ Aucun dev dans la whitelist.")
            return

        elif cleaned.startswith("!blocksite") and is_mod:
            parts = content.split()
            if len(parts) > 1:
                site = parts[1].lower()
                self.translator.add_blocked_site(site)
                await self.safe_send(
                    message.channel,
                    f"🚫 Site '{site}' bloqué ! "
                    f"Les bots contenant ce mot seront ban automatiquement.",
                )
            else:
                await self.safe_send(message.channel,  f"@{user} Usage: !blocksite <nom_site>")
            return

        elif cleaned.startswith("!unblocksite") and is_mod:
            parts = content.split()
            if len(parts) > 1:
                site = parts[1].lower()
                if self.translator.remove_blocked_site(site):
                    await self.safe_send(message.channel,  f"✅ Site '{site}' débloqué.")
                else:
                    await self.safe_send(message.channel,  f"ℹ️ '{site}' n'est pas bloqué.")
            else:
                await self.safe_send(message.channel,  f"@{user} Usage: !unblocksite <nom_site>")
            return

        elif cleaned.startswith("!blockedlist") and is_mod:
            sites = self.translator.get_blocked_sites()
            if sites:
                sites_str = ", ".join(sites)
                await self.safe_send(
                    message.channel, f"🚫 Sites bloqués ({len(sites)}): {sites_str}"
                )
            else:
                await self.safe_send(message.channel,  "ℹ️ Aucun site bloqué.")
            return

        # === AUTOMOD TWITCH COMMANDS (API) ===
        elif cleaned.startswith("!addbanword") and is_mod:
            if not self.automod_enabled:
                await self.safe_send(message.channel, "⚠️ AutoMod API désactivé (config/scopes manquants)")
                return
            
            parts = content.split()
            if len(parts) > 1:
                word = " ".join(parts[1:])  # Support phrases avec espaces
                print(f"[AUTOMOD] 📞 Appel API add_blocked_term pour '{word}'...")
                result = await self.automod.add_blocked_term(word)
                if result:
                    print(f"[AUTOMOD] ✅ Confirmation : mot '{word}' ajouté avec succès")
                    await self.safe_send(
                        message.channel,
                        f"🚫 Mot '{word}' ajouté à l'AutoMod Twitch ! "
                        f"Les messages avec ce mot seront bloqués automatiquement."
                    )
                else:
                    print(f"[AUTOMOD] ❌ Échec : mot '{word}' n'a pas pu être ajouté")
                    await self.safe_send(message.channel, "❌ Erreur lors de l'ajout (vérifier scopes OAuth).")
            else:
                await self.safe_send(message.channel, f"@{user} Usage: !addbanword <mot>")
            return

        elif cleaned.startswith("!removebanword") and is_mod:
            if not self.automod_enabled:
                await self.safe_send(message.channel, "⚠️ AutoMod API désactivé (config/scopes manquants)")
                return
            
            parts = content.split()
            if len(parts) > 1:
                word = " ".join(parts[1:])
                # Trouver l'ID du term par son texte
                term = await self.automod.find_blocked_term_by_text(word)
                if term:
                    success = await self.automod.remove_blocked_term(term["id"])
                    if success:
                        await self.safe_send(message.channel, f"✅ Mot '{word}' retiré de l'AutoMod.")
                    else:
                        await self.safe_send(message.channel, "❌ Erreur lors de la suppression.")
                else:
                    await self.safe_send(message.channel, f"ℹ️ '{word}' n'est pas dans la liste AutoMod.")
            else:
                await self.safe_send(message.channel, f"@{user} Usage: !removebanword <mot>")
            return

        elif cleaned.startswith("!banwords") and is_mod:
            if not self.automod_enabled:
                await self.safe_send(message.channel, "⚠️ AutoMod API désactivé (config/scopes manquants)")
                return
            
            terms = await self.automod.get_blocked_terms()
            if terms:
                words = [t["text"] for t in terms]
                words_str = ", ".join(words)
                await self.safe_send(
                    message.channel,
                    f"🚫 Mots bannis AutoMod ({len(words)}): {words_str}"
                )
            else:
                await self.safe_send(message.channel, "ℹ️ Aucun mot banni dans l'AutoMod.")
            return

        elif cleaned.startswith("!automod") and is_mod:
            if not self.automod_enabled:
                await self.safe_send(message.channel, "⚠️ AutoMod API désactivé (config/scopes manquants)")
                return
            
            parts = content.split()
            if len(parts) > 1 and parts[1].isdigit():
                level = int(parts[1])
                if 0 <= level <= 4:
                    success = await self.automod.set_automod_level(level)
                    if success:
                        levels_desc = ["Désactivé", "Faible", "Modéré", "Élevé", "Strict"]
                        await self.safe_send(
                            message.channel,
                            f"✅ AutoMod configuré: Niveau {level} ({levels_desc[level]})"
                        )
                    else:
                        await self.safe_send(message.channel, "❌ Erreur de configuration.")
                else:
                    await self.safe_send(message.channel, "⚠️ Niveau doit être 0-4")
            else:
                await self.safe_send(message.channel, f"@{user} Usage: !automod <0-4>")
            return

        # === BOT WHITELIST/BLACKLIST COMMANDS ===
        elif cleaned.startswith("!addwhitebot") and is_mod:
            parts = content.split()
            if len(parts) > 1:
                bot_name = parts[1].strip("@")
                self.translator.add_bot_to_whitelist(bot_name)
                await self.safe_send(
                    message.channel,
                    f"✅ Bot @{bot_name} ajouté à la whitelist ! "
                    f"SerdaBot ne lui répondra plus."
                )
            else:
                await self.safe_send(message.channel,  f"@{user} Usage: !addwhitebot @bot_name")
            return

        elif cleaned.startswith("!delwhitebot") and is_mod:
            parts = content.split()
            if len(parts) > 1:
                bot_name = parts[1].strip("@")
                if self.translator.remove_bot_from_whitelist(bot_name):
                    await self.safe_send(
                        message.channel, f"✅ Bot @{bot_name} retiré de la whitelist."
                    )
                else:
                    await self.safe_send(
                        message.channel, f"ℹ️ @{bot_name} n'est pas dans la whitelist."
                    )
            else:
                await self.safe_send(message.channel,  f"@{user} Usage: !delwhitebot @bot_name")
            return

        elif cleaned.startswith("!addblackbot") and is_mod:
            parts = content.split()
            if len(parts) > 1:
                bot_name = parts[1].strip("@")
                self.translator.add_bot_to_blacklist(bot_name)
                await self.safe_send(
                    message.channel,
                    f"🚫 Bot @{bot_name} ajouté à la blacklist ! "
                    f"SerdaBot ignorera tous ses messages."
                )
            else:
                await self.safe_send(message.channel,  f"@{user} Usage: !addblackbot @bot_name")
            return

        elif cleaned.startswith("!delblackbot") and is_mod:
            parts = content.split()
            if len(parts) > 1:
                bot_name = parts[1].strip("@")
                if self.translator.remove_bot_from_blacklist(bot_name):
                    await self.safe_send(
                        message.channel, f"✅ Bot @{bot_name} retiré de la blacklist."
                    )
                else:
                    await self.safe_send(
                        message.channel, f"ℹ️ @{bot_name} n'est pas dans la blacklist."
                    )
            else:
                await self.safe_send(message.channel,  f"@{user} Usage: !delblackbot @bot_name")
            return

        elif cleaned.startswith("!whitebots") and is_mod:
            bots = self.translator.get_whitelisted_bots()
            if bots:
                bots_str = ", ".join(f"@{b}" for b in bots)
                await self.safe_send(
                    message.channel, f"📋 Bots whitelistés ({len(bots)}): {bots_str}"
                )
            else:
                await self.safe_send(message.channel,  "ℹ️ Aucun bot dans la whitelist.")
            return

        elif cleaned.startswith("!blackbots") and is_mod:
            bots = self.translator.get_blacklisted_bots()
            if bots:
                bots_str = ", ".join(f"@{b}" for b in bots)
                await self.safe_send(
                    message.channel, f"🚫 Bots blacklistés ({len(bots)}): {bots_str}"
                )
            else:
                await self.safe_send(message.channel,  "ℹ️ Aucun bot dans la blacklist.")
            return

        # === TRADUCTION MANUELLE ===
        elif (cleaned.startswith("!translate ") or cleaned.startswith("!trad ")) and is_mod:
            # Extract text
            # Extract text
            text = (
                content_without_mention[11:].strip() if cleaned.startswith("!translate ") else content_without_mention[6:].strip()
            )
            if text:
                # Limite Twitch: ~500 chars max, on garde une marge
                MAX_INPUT_LENGTH = 200  # Limite input pour éviter débordement output
                if len(text) > MAX_INPUT_LENGTH:
                    await self.safe_send(
                        message.channel,
                        f"@{user} ⚠️ Texte trop long ({len(text)} chars). "
                        f"Limite: {MAX_INPUT_LENGTH} caractères pour la traduction."
                    )
                    return
                
                try:
                    # Detect language (simple heuristic)
                    has_french = any(
                        word in text.lower()
                        for word in ["le", "la", "les", "de", "du", "un", "une"]
                    )
                    source = "fr" if has_french else "en"
                    target = "en" if source == "fr" else "fr"

                    translated = self.translator.translate(text, source, target)
                    if translated and not translated.startswith("⚠️"):
                        # flag_source = "🇫🇷" if source == "fr" else "🇬🇧"  # Unused for now
                        flag_target = "🇬🇧" if source == "fr" else "🇫🇷"
                        
                        # Format compact pour éviter overflow
                        response = f"{flag_target} {translated}"
                        
                        # Sécurité finale: tronquer si trop long
                        if len(response) > 480:
                            response = response[:477] + "…"
                        
                        await self.safe_send(message.channel, response)
                    elif translated and translated.startswith("⚠️"):
                        # Erreur de traduction avec message informatif
                        await self.safe_send(message.channel,  f"@{user} {translated}")
                    else:
                        await self.safe_send(
                            message.channel, f"@{user} ❌ Service de traduction indisponible."
                        )
                except (RuntimeError, ValueError, KeyError) as e:
                    print(f"❌ Erreur traduction manuelle: {e}")
                    await self.safe_send(
                        message.channel, f"@{user} ❌ Erreur critique de traduction."
                    )
            else:
                await self.safe_send(message.channel,  f"@{user} Usage: !translate <texte>")
            return

        if cleaned.startswith("!gameinfo ") and "game" in self.enabled:
            game_name = content_without_mention[10:].strip()
            await self.run_with_cooldown(
                user, lambda: handle_game_command(message, self.config, game_name, now, bot=self)
            )

        elif cleaned.startswith("!ask") and "ask" in self.enabled:
            query = content_without_mention[4:].strip()
            if query == "":
                await self.safe_send(
                    message.channel,
                    f"@{user} Tu as oublié de poser ta question. "
                    f"Utilise la commande `!ask ta_question`.",
                )
                return
            await self.run_with_cooldown(
                user, lambda: handle_ask_command(message, self.config, query, now, llm_available=self.llm_available, bot=self)
            )

        elif cleaned.startswith("!cacheadd "):
            # Commande admin: ajouter un fait au cache
            args = content_without_mention[10:].strip()
            await handle_cacheadd_command(message, self.config, args)

        elif cleaned == "!cachestats":
            # Commande admin: statistiques du cache
            await handle_cachestats_command(message, self.config)

        elif cleaned == "!cacheclear":
            # Commande admin: vider le cache (DANGER)
            await handle_cacheclear_command(message, self.config)

        elif cleaned.startswith("!donationserda") or cleaned.startswith("!serdakofi"):
            await self.run_with_cooldown(
                user, lambda: handle_donation_command(message, self.config, now)
            )

        elif is_mentioned and "chill" in self.enabled:
            await self.run_with_cooldown(
                user, lambda: handle_chill_command(message, self.config, now, conversation_manager=self.conversation_manager, llm_available=self.llm_available, bot=self, translator=self.translator)
            )

    async def safe_send(self, channel, content):
        """Envoie un message de manière sécurisée avec gestion des erreurs.

        Utilise l'API Send Chat Message (badge bot 🤖) avec fallback IRC.

        Args:
            channel: Le canal où envoyer le message
            content: Le contenu du message à envoyer
        """
        if len(content) > 500:
            content = content[:497] + "..."
        
        # Essayer l'API d'abord (badge bot 🤖)
        if self.api_enabled:
            try:
                print(f"[API] 📤 Tentative d'envoi via API: {content[:100]}...")
                success = await self.api_sender.send_message(content, use_badge=True)
                if success:
                    print("[API] ✅ Message envoyé avec badge bot!")
                    return
                else:
                    print("[API] ⚠️ Échec API, fallback vers IRC...")
            except Exception as e:
                print(f"[API] ❌ Exception API: {e}, fallback vers IRC...")
        
        # Fallback IRC si API désactivée ou échouée
        try:
            print(f"[IRC] 📤 Envoi via IRC: {content[:100]}...")
            await channel.send(content)
            print("[IRC] ✅ Message envoyé!")
        except ConnectionError as e:
            print(f"❌ Erreur de connexion lors de l'envoi: {e}")
        except TimeoutError as e:
            print(f"❌ Délai dépassé lors de l'envoi: {e}")
        except (ValueError, RuntimeError) as e:
            print(f"❌ Erreur d'envoi du message: {e}")

    async def event_reconnect(self):
        """Événement appelé par TwitchIO quand le serveur IRC envoie RECONNECT.
        
        TwitchIO 2.x reconnecte automatiquement après cet événement.
        L'annonce sera faite dans event_channel_joined() au retour.
        """
        print("\n" + "="*60)
        print("[RECONNECT] 📨 Message RECONNECT reçu de Twitch")
        print("[RECONNECT] ⏳ TwitchIO va reconnecter automatiquement...")
        print("="*60 + "\n")
    
    async def event_error(self, error, data=None):
        """Filet de sécurité: détecte et log les erreurs.
        
        Les erreurs réseau déclenchent une reconnexion auto de TwitchIO.
        L'annonce sera faite dans event_channel_joined() au retour.
        """
        exc_name = type(error).__name__ if error else "Unknown"
        print(f"[ERROR] ⚠️ Erreur détectée: {exc_name}")
        
        # Log spécifique pour les erreurs réseau
        if any(k in exc_name for k in ("ConnectionClosed", "WebSocket", "Timeout", "ConnectionError")):
            print(f"[ERROR] 🔌 Erreur de connexion → TwitchIO va reconnecter automatiquement")
        
        # Affiche l'erreur pour debug
        if error:
            import traceback
            traceback.print_exception(type(error), error, error.__traceback__)
    
    async def event_channel_joined(self, channel):
        """Événement appelé quand le bot (re)joint un salon (TwitchIO 2.10+).
        
        C'est ici qu'on annonce le retour après une reconnexion.
        """
        print(f"[JOIN] ✅ Bot rejoint le salon: {channel.name}")
        
        # Si c'est la première fois qu'on joint, on marque juste
        if not self._channel_joined_once:
            self._channel_joined_once = True
            print("[JOIN] 📍 Première connexion au salon")
            return
        
        # Si on avait déjà joint avant, c'est une RECONNEXION
        if self._booted:
            print("[RECONNECT] 🎉 Reconnexion détectée! Annonce dans le chat...")
            
            # Cooldown anti-spam
            now = datetime.now().timestamp()
            cooldown = self.config.get("reconnect_announce_cooldown", 10)
            if now - self._last_reconnect_announce < cooldown:
                print(f"[RECONNECT] ⏳ Cooldown actif ({cooldown}s), message ignoré")
                return
            
            self._last_reconnect_announce = now
            try:
                await channel.send("Me revoilà, petite coupure de connexion ! 🔌")
                print("[RECONNECT] ✅ Message envoyé avec succès")
            except Exception as e:
                print(f"[RECONNECT] ❌ Impossible d'envoyer le message: {e}")
    


def run_bot(config):
    """Lance le bot Twitch avec la configuration donnée."""
    async def main():
        bot = TwitchBot(config)
        await bot.start()

    asyncio.run(main())

if __name__ == "__main__":
    try:
        run_bot(CONFIG)
    except Exception as e:
        print(f"[CRITICAL] Une erreur critique s'est produite : {e}")
        traceback.print_exc()

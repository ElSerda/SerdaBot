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
import traceback
from datetime import datetime, timedelta

from twitchio.ext import commands  # type: ignore

from src.config.config import load_config
from src.core.commands.ask_command import handle_ask_command
from src.core.commands.chill_command import handle_chill_command
from src.core.commands.donation_command import handle_donation_command
from src.core.commands.game_command import handle_game_command
from src.utils.translator import Translator

CONFIG = load_config()


class TwitchBot(commands.Bot):  # pyright: ignore[reportPrivateImportUsage]
    """Bot Twitch personnalisé avec gestion des commandes et de la traduction automatique.

    Cette classe étend le Bot TwitchIO standard avec des fonctionnalités personnalisées
    comme la traduction automatique, la gestion du spam et diverses commandes utilitaires.
    """

    def __init__(self, config):
        super().__init__(
            token=config["twitch"]["token"],
            prefix="!",
            initial_channels=[config["bot"]["channel"]],
        )
        self.config = config
        self.cooldowns = {}
        self.botname = config["bot"]["name"].lower()
        self.enabled = config["bot"].get("enabled_commands", [])

        # Initialize translator
        self.translator = Translator()
        self.auto_translate = config["bot"].get("auto_translate", True)

    async def event_ready(self):
        print(f'\n🤖 Connected to Twitch chat as {self.nick}')
        self._display_model_config()
        print("☕️ Boot complete.")
        print("🤖 SerdaBot is online and ready.")
        
        # Send connect message if configured
        connect_message = self.config["bot"].get("connect_message", "").strip()
        if connect_message and self.connected_channels:
            await self.safe_send(self.connected_channels[0], connect_message)

    def _display_model_config(self):
        """Affiche la configuration du modèle au démarrage.

        Cette méthode privée affiche les informations de configuration du modèle, notamment :
        - L'endpoint utilisé (LM Studio, FastAPI, ou externe)
        - Le modèle OpenAI de fallback si configuré
        - La liste des commandes activées
        """
        print("\n🧠 === CONFIGURATION MODÈLE ===")

        # Endpoint externe (LM Studio/FastAPI)
        endpoint = self.config["bot"].get("model_endpoint") or self.config["bot"].get("api_url")
        if endpoint:
            endpoint_type = (
                "LM Studio"
                if "1234" in endpoint
                else "FastAPI" if "8000" in endpoint else "Externe"
            )
            print(f"� {endpoint_type}: {endpoint}")

        # OpenAI fallback
        if self.config["bot"].get("model_type") == "openai":
            model = self.config["bot"].get("openai_model", "gpt-3.5-turbo")
            print(f"🌐 Fallback: OpenAI ({model})")

        # Commandes activées
        enabled = self.config["bot"].get("enabled_commands", [])
        print(f"⚡ Commandes: {', '.join(enabled)}")
        print("=" * 35)

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
        cleaned = re.sub(r"[^\w\s!?]", "", content.lower())

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
            text = (
                content[11:].strip() if cleaned.startswith("!translate ") else content[6:].strip()
            )
            if text:
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
                        flag_source = "🇫🇷" if source == "fr" else "🇬🇧"
                        flag_target = "🇬🇧" if source == "fr" else "🇫🇷"
                        await self.safe_send(
                            message.channel, f"{flag_source} {text}\n{flag_target} {translated}"
                        )
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
            game_name = content[10:].strip()
            await self.run_with_cooldown(
                user, lambda: handle_game_command(message, self.config, game_name, now)
            )

        elif cleaned.startswith("!ask") and "ask" in self.enabled:
            query = content[4:].strip()
            if query == "":
                await self.safe_send(
                    message.channel,
                    f"@{user} Tu as oublié de poser ta question. "
                    f"Utilise la commande `!ask ta_question`.",
                )
                return
            await self.run_with_cooldown(
                user, lambda: handle_ask_command(message, self.config, query, now)
            )

        elif cleaned.startswith("!donationserda") or cleaned.startswith("!serdakofi"):
            # Commandes de donation/support spécifiques à El_Serda
            await self.run_with_cooldown(
                user, lambda: handle_donation_command(message, self.config, now)
            )

        elif self.botname in cleaned and "chill" in self.enabled:
            # Mention du bot → Mode chill fun/cool (réponses ultra-courtes 1-5 mots)
            words = re.findall(r"\b\w+\b", cleaned)
            if self.botname in words:
                await self.run_with_cooldown(
                    user, lambda: handle_chill_command(message, self.config, now)
                )

    async def safe_send(self, channel, content):
        """Envoie un message de manière sécurisée avec gestion des erreurs.

        Args:
            channel: Le canal où envoyer le message
            content: Le contenu du message à envoyer
        """
        if len(content) > 500:
            content = content[:497] + "..."
        try:
            print(f"[SEND] 📤 Tentative d'envoi: {content[:100]}...")
            await channel.send(content)
            print("[SEND] ✅ Message envoyé avec succès!")
        except ConnectionError as e:
            print(f"❌ Erreur de connexion lors de l'envoi: {e}")
        except TimeoutError as e:
            print(f"❌ Délai dépassé lors de l'envoi: {e}")
        except (ValueError, RuntimeError) as e:
            print(f"❌ Erreur d'envoi du message: {e}")


def run_bot(config):
    """Lance le bot Twitch avec la configuration donnée.

    Args:
        config: La configuration du bot (chargée depuis config.yaml)
    """

    async def main():
        """Fonction principale asynchrone pour démarrer le bot."""
        bot = TwitchBot(config)
        await bot.start()

    asyncio.run(main())


if __name__ == "__main__":
    run_bot(CONFIG)

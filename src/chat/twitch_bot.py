import asyncio
import re
import sys
import os
from datetime import datetime, timedelta

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from twitchio import Message
from twitchio.ext import commands

from config.config import load_config
from core.commands.ask_command import handle_ask_command
from core.commands.chill_command import handle_chill_command
from core.commands.game_command import handle_game_command
from core.commands.donation_command import handle_donation_command
from utils.translator import Translator

config = load_config()


class TwitchBot(commands.Bot):
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
        print(
            f'\n🤖 Connected to Twitch chat as {self.nick} (channel: {self.config["bot"]["channel"]})'
        )
        
        # Affichage de la configuration du modèle
        self._display_model_config()
        
        print("☕️ Boot complete.")
        print("🤖 SerdaBot is online and ready.")
        if self.connected_channels:
            await self.safe_send(self.connected_channels[0], "My body is ready ! ☕")
    
    def _display_model_config(self):
        """Affiche la configuration du modèle au démarrage"""
        print("\n🧠 === CONFIGURATION MODÈLE ===")
        
        # Endpoint externe (LM Studio/FastAPI)
        endpoint = self.config["bot"].get("model_endpoint") or self.config["bot"].get("api_url")
        if endpoint:
            endpoint_type = "LM Studio" if "1234" in endpoint else "FastAPI" if "8000" in endpoint else "Externe"
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
        try:
            await action()
        except Exception as e:
            print(f"❌ Erreur dans la commande de @{user} : {e}")
        finally:
            self.cooldowns[user] = datetime.now()
            print(
                f'[{datetime.now().strftime("%H:%M:%S")}] ✅ Prêt à écouter de nouvelles commandes.'
            )

    async def event_message(self, message: Message):
        if message.echo:
            return

        content = str(message.content).strip()
        user = str(message.author.name or "user").lower()
        now = datetime.now()
        cooldown = self.config["bot"].get("cooldown", 60)
        cleaned = re.sub(r"[^\w\s!?]", "", content.lower())
        
        # === SPAM BOT DETECTION & BAN ===
        channel_owner = message.channel.name.lower()
        if self.translator.is_spam_bot(user, content, channel_owner):
            print(f"🚫 Spam bot détecté: {user} - Message: {content[:50]}")
            try:
                # Timeout le bot spam (60s = 1min) - Via commande chat
                timeout_command = f"/timeout {user} 60"
                await message.channel.send(timeout_command)
                print(f"✅ Commande timeout envoyée: {user} (60 sec)")
            except Exception as e:
                print(f"❌ Échec timeout de {user}: {e}")
            return
        else:
            # Log pour debug (optionnel)
            print(f"💬 Message de {user}: {content[:30]}... [OK]")
        
        # === AUTO-TRADUCTION DEVS ===
        if self.auto_translate and self.translator.should_translate(user, content):
            try:
                translated = self.translator.translate(content, 'en', 'fr')
                if translated and not translated.startswith("⚠️"):
                    formatted = f"🌐 @{user}: {content}\n└─ 🇫🇷 {translated}"
                    await self.safe_send(message.channel, formatted)
                elif translated and translated.startswith("⚠️"):
                    # Erreur de traduction, mais on affiche quand même un message d'info
                    await self.safe_send(message.channel, f"🌐 @{user}: {content}\n└─ {translated}")
            except Exception as e:
                print(f"❌ Erreur auto-traduction pour {user}: {e}")
                # En cas d'erreur critique, on affiche juste le message original
                await self.safe_send(message.channel, f"🌐 @{user}: {content}\n└─ ⚠️ Traduction indisponible")
        
        # Check cooldown
        if user in self.cooldowns and now - self.cooldowns[user] < timedelta(
            seconds=cooldown
        ):
            return
        
        # === COMMANDES TRADUCTION (MOD ONLY) ===
        is_mod = message.author.is_mod or user == message.channel.name.lower()
        
        if cleaned.startswith("!adddev") and is_mod:
            parts = content.split()
            if len(parts) > 1:
                username = parts[1].strip('@')
                self.translator.add_dev(username)
                await self.safe_send(message.channel, f"✅ @{username} ajouté à la whitelist traduction !")
            else:
                await self.safe_send(message.channel, f"@{user} Usage: !adddev @username")
            return
        
        elif (cleaned.startswith("!removedev") or cleaned.startswith("!deldev")) and is_mod:
            parts = content.split()
            if len(parts) > 1:
                username = parts[1].strip('@')
                if self.translator.remove_dev(username):
                    await self.safe_send(message.channel, f"✅ @{username} retiré de la whitelist.")
                else:
                    await self.safe_send(message.channel, f"ℹ️ @{username} n'est pas dans la whitelist.")
            else:
                cmd_used = "!deldev" if cleaned.startswith("!deldev") else "!removedev"
                await self.safe_send(message.channel, f"@{user} Usage: {cmd_used} @username")
            return
        
        elif cleaned.startswith("!listdevs") and is_mod:
            devs = self.translator.get_devs()
            if devs:
                devs_str = ", ".join(f"@{d}" for d in devs)
                await self.safe_send(message.channel, f"📋 Devs whitelistés ({len(devs)}): {devs_str}")
            else:
                await self.safe_send(message.channel, "ℹ️ Aucun dev dans la whitelist.")
            return
        
        elif cleaned.startswith("!blocksite") and is_mod:
            parts = content.split()
            if len(parts) > 1:
                site = parts[1].lower()
                self.translator.add_blocked_site(site)
                await self.safe_send(message.channel, f"🚫 Site '{site}' bloqué ! Les bots contenant ce mot seront ban automatiquement.")
            else:
                await self.safe_send(message.channel, f"@{user} Usage: !blocksite <nom_site>")
            return
        
        elif cleaned.startswith("!unblocksite") and is_mod:
            parts = content.split()
            if len(parts) > 1:
                site = parts[1].lower()
                if self.translator.remove_blocked_site(site):
                    await self.safe_send(message.channel, f"✅ Site '{site}' débloqué.")
                else:
                    await self.safe_send(message.channel, f"ℹ️ '{site}' n'est pas bloqué.")
            else:
                await self.safe_send(message.channel, f"@{user} Usage: !unblocksite <nom_site>")
            return
        
        elif cleaned.startswith("!blockedlist") and is_mod:
            sites = self.translator.get_blocked_sites()
            if sites:
                sites_str = ", ".join(sites)
                await self.safe_send(message.channel, f"🚫 Sites bloqués ({len(sites)}): {sites_str}")
            else:
                await self.safe_send(message.channel, "ℹ️ Aucun site bloqué.")
            return
        
        elif (cleaned.startswith("!translate ") or cleaned.startswith("!trad ")) and is_mod:
            # Extract text
            text = content[11:].strip() if cleaned.startswith("!translate ") else content[6:].strip()
            if text:
                try:
                    # Detect language (simple heuristic)
                    has_french = any(word in text.lower() for word in ['le', 'la', 'les', 'de', 'du', 'un', 'une'])
                    source = 'fr' if has_french else 'en'
                    target = 'en' if source == 'fr' else 'fr'
                    
                    translated = self.translator.translate(text, source, target)
                    if translated and not translated.startswith("⚠️"):
                        flag_source = "🇫🇷" if source == 'fr' else "🇬🇧"
                        flag_target = "🇬🇧" if source == 'fr' else "🇫🇷"
                        await self.safe_send(message.channel, f"{flag_source} {text}\n{flag_target} {translated}")
                    elif translated and translated.startswith("⚠️"):
                        # Erreur de traduction avec message informatif
                        await self.safe_send(message.channel, f"@{user} {translated}")
                    else:
                        await self.safe_send(message.channel, f"@{user} ❌ Service de traduction indisponible.")
                except Exception as e:
                    print(f"❌ Erreur traduction manuelle: {e}")
                    await self.safe_send(message.channel, f"@{user} ❌ Erreur critique de traduction.")
            else:
                await self.safe_send(message.channel, f"@{user} Usage: !translate <texte>")
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
                    f"@{user} Tu as oublié de poser ta question. Utilise la commande `!ask ta_question`.",
                )
                return
            await self.run_with_cooldown(
                user, lambda: handle_ask_command(message, self.config, query, now)
            )

        elif (cleaned.startswith("!donationserda") or cleaned.startswith("!serdakofi")):
            # Commandes de donation/support spécifiques à El_Serda
            await self.run_with_cooldown(
                user, lambda: handle_donation_command(message, self.config, now)
            )

        elif self.botname in cleaned and "chill" in self.enabled:
            # Mention du bot → Mode sarcastique El_Serda (seule façon d'activer chill)
            words = re.findall(r"\b\w+\b", cleaned)
            if self.botname in words:
                await self.run_with_cooldown(
                    user, lambda: handle_chill_command(message, self.config, now)
                )

    async def safe_send(self, channel, content):
        if len(content) > 500:
            content = content[:497] + "..."
        try:
            print(f"[SEND] 📤 Tentative d'envoi: {content[:100]}...")
            await channel.send(content)
            print(f"[SEND] ✅ Message envoyé avec succès!")
        except Exception as e:
            print(f"❌ Failed to send message: {e}")


def run_bot(config):
    async def main():
        bot = TwitchBot(config)
        await bot.start()

    asyncio.run(main())


if __name__ == "__main__":
    run_bot(config)

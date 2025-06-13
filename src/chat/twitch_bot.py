import asyncio
import re
from datetime import datetime, timedelta

from twitchio import Message
from twitchio.ext import commands

from config.config import load_config
from core.commands.ask_command import handle_ask_command
from core.commands.chill_command import handle_chill_command
from core.commands.game_command import handle_game_command

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

    async def event_ready(self):
        print(
            f'\n🤖 Connected to Twitch chat as {self.nick} (channel: {self.config["bot"]["channel"]})'
        )
        print("☕️ Boot complete.")
        print("🤖 SerdaBot is online and ready.")
        if self.connected_channels:
            await self.safe_send(self.connected_channels[0], "☕️")

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

        if user in self.cooldowns and now - self.cooldowns[user] < timedelta(
            seconds=cooldown
        ):
            return

        if cleaned.startswith("!game ") and "game" in self.enabled:
            game_name = content[6:].strip()
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

        elif self.botname in cleaned and "chill" in self.enabled:
            words = re.findall(r"\b\w+\b", cleaned)
            if self.botname in words:
                await self.run_with_cooldown(
                    user, lambda: handle_chill_command(message, self.config, now)
                )

    async def safe_send(self, channel, content):
        if len(content) > 500:
            content = content[:497] + "..."
        try:
            await channel.send(content)
        except Exception as e:
            print(f"❌ Failed to send message: {e}")


def run_bot(config):
    async def main():
        bot = TwitchBot(config)
        await bot.start()

    asyncio.run(main())


if __name__ == "__main__":
    run_bot(config)

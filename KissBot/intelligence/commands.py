"""
Intelligence Commands Component - !ask
"""

from twitchio.ext import commands
from intelligence import LLMHandler
from intelligence.core import process_llm_request, extract_question_from_command


class IntelligenceCommands(commands.Cog):
    """Commandes IA."""
    
    def __init__(self, bot):
        self.bot = bot
        self.llm_handler = LLMHandler(bot.config)
        # Update bot name avec le vrai nom TwitchIO (après connexion)
        if hasattr(bot, 'nick') and bot.nick:
            self.llm_handler.update_bot_name(bot.nick)
    
    @commands.command(name='ask')
    async def ask_command(self, ctx: commands.Context):
        """Pose une question à l'IA."""
        # 📦 Extraction question
        question = extract_question_from_command(ctx.message.content)
        if not question:
            await ctx.send("Usage: !ask <question>")
            return
        
        # ⏱️ Rate limit check
        if not self.bot.rate_limiter.is_allowed(ctx.author.name, cooldown=10.0):
            remaining = self.bot.rate_limiter.get_remaining_cooldown(ctx.author.name, cooldown=10.0)
            await ctx.send(f"@{ctx.author.name} Cooldown! Attends {remaining:.1f}s")
            return
        
        # 🧠 Logique métier (testable)
        response = await process_llm_request(
            llm_handler=self.llm_handler,
            prompt=question,
            context="ask",
            user_name=ctx.author.name
        )
        
        # 💬 Réponse Twitch
        if not response:
            await ctx.send(f"@{ctx.author.name} Erreur IA, réessaye plus tard")
        else:
            await ctx.send(f"@{ctx.author.name} {response}")


def prepare(bot):
    """Setup function for TwitchIO."""
    bot.add_cog(IntelligenceCommands(bot))

"""
Intelligence Events - @mention handler
"""

from intelligence.core import process_llm_request, extract_mention_message


async def handle_mention(bot, message):
    """
    Traite les @mention du bot dans le chat.
    
    Args:
        bot: Instance du bot
        message: Message TwitchIO
    
    Returns:
        str: Réponse générée ou None
    """
    # 📦 Extraction message
    bot.logger.info(f"🔍 Extraction: message='{message.content}', bot_name='{bot.nick}'")
    user_message = extract_mention_message(message.content, bot.nick)
    bot.logger.info(f"🔍 User message extrait: '{user_message}'")
    
    if not user_message:
        bot.logger.warning(f"⚠️ Extraction échouée ! Message vide après extraction.")
        return None
    
    # ⏱️ Rate limit check déjà fait dans bot.py - pas besoin ici
    # if not bot.rate_limiter.is_allowed(message.author.name, cooldown=15.0):
    #     remaining = bot.rate_limiter.get_remaining_cooldown(message.author.name, cooldown=15.0)
    #     return f"@{message.author.name} Cooldown! Attends {remaining:.1f}s"
    
    # 🧠 Logique métier (testable) - Récupérer LLMHandler partagé
    bot.logger.info(f"🔍 Cogs disponibles: {list(bot.cogs.keys())}")
    intelligence_cog = bot.get_cog('IntelligenceCommands')
    bot.logger.info(f"🔍 Intelligence Cog trouvé: {intelligence_cog is not None}")
    
    if not intelligence_cog:
        bot.logger.error("IntelligenceCommands Cog not loaded!")
        return f"@{message.author.name} Erreur IA 😵"
    
    response = await process_llm_request(
        llm_handler=intelligence_cog.llm_handler,
        prompt=user_message,
        context="mention",
        user_name=message.author.name
    )
    
    # 💬 Réponse Twitch
    if not response:
        return f"@{message.author.name} Erreur IA 😵"
    
    return f"@{message.author.name} {response}"

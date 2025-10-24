"""
Intelligence Core - Logique métier pure (facile à tester)
Séparation business logic / framework TwitchIO
"""

from typing import Optional


async def process_llm_request(
    llm_handler,
    prompt: str,
    context: str,
    user_name: str
) -> Optional[str]:
    """
    Traite une requête LLM - Logique métier pure.
    
    Args:
        llm_handler: Instance LLMHandler
        prompt: Question/message de l'utilisateur
        context: Context ("ask" ou "mention")
        user_name: Nom de l'utilisateur
    
    Returns:
        str: Réponse formatée (tronquée si nécessaire) ou None si erreur
    """
    try:
        response = await llm_handler.generate_response(
            prompt=prompt,
            context=context,
            user_name=user_name
        )
        
        if not response:
            return None
        
        # Truncate si trop long (Twitch limit: 500 chars, on laisse marge)
        if len(response) > 450:
            response = response[:447] + "..."
        
        return response
        
    except Exception as e:
        # Log l'erreur mais ne crash pas
        return None


def extract_question_from_command(message_content: str) -> Optional[str]:
    """
    Extrait la question d'une commande !ask.
    
    Args:
        message_content: Contenu complet du message "!ask <question>"
    
    Returns:
        str: Question extraite ou None si invalide
    """
    parts = message_content.strip().split(maxsplit=1)
    if len(parts) < 2:
        return None
    return parts[1].strip()


def extract_mention_message(message_content: str, bot_name: str) -> Optional[str]:
    """
    Extrait le message d'une mention @bot ou bot_name.
    
    Args:
        message_content: Contenu complet du message "@bot <message>" ou "bot_name <message>"
        bot_name: Nom du bot (case-insensitive)
    
    Returns:
        str: Message extrait ou None si invalide
    """
    content_lower = message_content.lower()
    bot_lower = bot_name.lower()
    
    # Chercher @bot_name ou bot_name seul
    if f"@{bot_lower}" in content_lower:
        # Format @bot_name
        mention = f"@{bot_name}"
    elif bot_lower in content_lower:
        # Format bot_name seul
        mention = bot_name
    else:
        return None
    
    # Extraire le texte en retirant la mention
    # Supporte: "bot_name message", "message bot_name", "@bot_name message"
    message = message_content.replace(f"@{bot_name}", "", 1)
    message = message.replace(bot_name, "", 1)
    message = message.strip()
    
    return message if message else None

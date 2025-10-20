"""
Command handler for game playtime lookup (!temps).

Commande simple et rapide pour obtenir la durée de jeu estimée.
"""
from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from .api import fetch_game_playtime, format_playtime_message


async def handle_temps_command(
    message: Message, 
    config: dict, 
    game_name: str, 
    now
):  # pylint: disable=unused-argument
    """
    Handler de la commande !temps.
    
    Récupère la durée de jeu estimée via HowLongToBeat.
    
    Args:
        message: Message Twitch
        config: Configuration globale du bot
        game_name: Nom du jeu recherché
        now: Timestamp actuel (unused)
    
    Example:
        !temps Hades
        → "@user ⏱️ Hades: 22h (histoire) | 95h (100%) (60s)"
    """
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)
    cooldown = config["bot"].get("cooldown", 60)
    
    # Validation
    if not game_name.strip():
        await message.channel.send(
            f"@{user} Tu as oublié de spécifier un jeu. Utilise `!temps nom_du_jeu`."
        )
        if debug:
            print(f"[TEMPS] ⚠️ Requête vide ignorée de @{user}")
        return
    
    await message.channel.send("⏱️ Recherche de la durée...")
    
    try:
        # Récupération de la durée
        data = await fetch_game_playtime(game_name)
        
        if not data:
            await message.channel.send(
                f"❌ Durée introuvable pour : {game_name}"
            )
            if debug:
                print(f"[TEMPS] ❌ Aucun résultat pour '{game_name}'")
            return
        
        # Formatage du message
        base_msg = await format_playtime_message(data)
        msg = f"@{user} {base_msg} ({cooldown}s)"
        
        await message.channel.send(msg)
        
        if debug:
            print(f"[TEMPS] ✅ Durée envoyée: {data.get('main_story', '?')} (histoire)")
    
    except (RuntimeError, ValueError, KeyError, TypeError) as e:
        await message.channel.send(
            f"@{user} ⚠️ Erreur lors de la recherche de la durée."
        )
        print(f"❌ [TEMPS] Exception : {e}")

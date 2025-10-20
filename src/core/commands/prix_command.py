"""
Command handler for game price lookup (!prix).

Commande simple et rapide pour obtenir le prix d'un jeu PC.
"""
from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from .api import fetch_game_price


async def handle_prix_command(
    message: Message, 
    config: dict, 
    game_name: str, 
    now
):  # pylint: disable=unused-argument
    """
    Handler de la commande !prix.
    
    Récupère le prix d'un jeu PC via CheapShark.
    
    Args:
        message: Message Twitch
        config: Configuration globale du bot
        game_name: Nom du jeu recherché
        now: Timestamp actuel (unused)
    
    Example:
        !prix Hades
        → "@user 💰 Hades: 20,99€ sur Steam (-15%) (60s)"
    """
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)
    cooldown = config["bot"].get("cooldown", 60)
    
    # Validation
    if not game_name.strip():
        await message.channel.send(
            f"@{user} Tu as oublié de spécifier un jeu. Utilise `!prix nom_du_jeu`."
        )
        if debug:
            print(f"[PRIX] ⚠️ Requête vide ignorée de @{user}")
        return
    
    await message.channel.send("💰 Recherche du prix...")
    
    try:
        # Récupération du prix
        data = await fetch_game_price(game_name)
        
        if not data:
            await message.channel.send(f"❌ Prix introuvable pour : {game_name}")
            if debug:
                print(f"[PRIX] ❌ Aucun résultat pour '{game_name}'")
            return
        
        # Formatage du message
        game = data['game_name']
        price = data['price']
        store = data['store']
        savings = data.get('savings')
        url = data.get('url', '')
        
        # Message de base
        msg = f"@{user} 💰 {game}: {price} sur {store}"
        
        # Ajouter la réduction si applicable
        if savings and price != "Gratuit":
            msg += f" (-{savings})"
        
        # Ajouter lien et cooldown
        if url:
            msg += f" ({url})"
        msg += f" ({cooldown}s)"
        
        await message.channel.send(msg)
        
        if debug:
            print(f"[PRIX] ✅ Prix envoyé: {price} sur {store}")
            if savings:
                print(f"[PRIX] 🎉 Réduction: -{savings}")
    
    except (RuntimeError, ValueError, KeyError, TypeError) as e:
        await message.channel.send(f"@{user} ⚠️ Erreur lors de la recherche du prix.")
        print(f"❌ [PRIX] Exception : {e}")

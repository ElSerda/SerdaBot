"""Command handler for !ask - AI-powered question answering."""

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from prompts.prompt_loader import make_prompt
from utils.model_utils import call_model
from src.utils.cache_manager import get_cached_or_fetch


async def handle_ask_command(message: Message, config: dict, question: str, now):  # pylint: disable=unused-argument
    """Handle the !ask command to answer user questions using AI."""
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)

    if not question.strip():
        await message.channel.send(
            f"@{user} Tu as oublié de poser ta question après `!ask`."
        )
        if debug:
            print(f"[ASK] ⚠️ Question vide reçue de @{user}")
        return

    if debug:
        print(f"[ASK] 🔎 Traitement de la question de @{user}...")

    # 1. Vérifier cache + Wikipedia d'abord
    cached_answer = await get_cached_or_fetch(question)
    if cached_answer:
        if debug:
            print(f"[ASK] 💡 Réponse depuis cache/Wikipedia")
        
        # Sécurité Twitch (500 chars max absolu avec @mention)
        final_response = cached_answer.strip()
        if len(final_response) > 480:
            final_response = final_response[:477] + "…"
        
        try:
            if debug:
                print(f"[SEND] 📤 Envoi CACHE: {final_response[:100]}...")
            await message.channel.send(f"@{user} {final_response}")
            if debug:
                print(f"[SEND] ✅ Envoyé avec succès (cache)")
        except Exception as e:
            print(f"[SEND] ❌ Erreur envoi: {e}")
        return

    # 2. Appel au modèle si pas dans cache (dernier recours)
    if debug:
        print(f"[ASK] 🤖 Appel modèle local...")
    
    # Récupérer game/title depuis config (si disponible)
    game = config.get("stream", {}).get("game")
    title = config.get("stream", {}).get("title")

    # Construire le prompt avec make_prompt
    prompt = make_prompt(mode="ask", content=question, user=user, game=game, title=title)
    
    if debug:
        print(f"[ASK] 📝 USER Prompt ({len(prompt)} chars): {prompt[:150]}{'...' if len(prompt) > 150 else ''}")
    
    response = await call_model(prompt, config, user=user, mode="ask")

    if not response:
        await message.channel.send(f"@{user} ⚠️ Erreur ou pas de réponse.")
        return

    # Sécurité Twitch (500 chars max absolu avec @mention)
    final_response = response.strip()
    if len(final_response) > 480:
        final_response = final_response[:477] + "…"

    try:
        if debug:
            print(f"[SEND] 📤 Envoi ASK: {final_response[:100]}...")
        await message.channel.send(f"@{user} {final_response}")
        if debug:
            print(f"[ASK] ✅ Réponse envoyée à @{user}")
    except Exception as e:
        print(f"[ASK] ❌ Erreur d'envoi: {e}")

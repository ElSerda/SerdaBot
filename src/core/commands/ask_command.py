"""Command handler for !ask - AI-powered question answering."""

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from prompts.prompt_loader import make_prompt
from utils.ask_utils import call_model


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

    # Message "Recherche en cours" supprimé pour économiser la limite de rate du bot non vérifié
    if debug:
        print(f"[ASK] 🔎 Traitement de la question de @{user}...")

    # Récupérer game/title depuis config (si disponible)
    game = config.get("stream", {}).get("game")
    title = config.get("stream", {}).get("title")

    # Construire le prompt avec make_prompt
    prompt = make_prompt(mode="ask", content=question, user=user, game=game, title=title)
    
    response = await call_model(prompt, config, user=user)

    if not response:
        await message.channel.send(f"@{user} ⚠️ Erreur ou pas de réponse.")
        return

    final_response = response.strip()
    if len(final_response) > 500:
        final_response = final_response[:497] + "…"

    await message.channel.send(f"@{user} {final_response}")

    if debug:
        print(f"[ASK] ✅ Réponse envoyée à @{user}")

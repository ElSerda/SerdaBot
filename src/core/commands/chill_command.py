"""Command handler for chill/sarcastic bot responses."""

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from prompts.prompt_loader import make_prompt
from utils.model_utils import call_model


def filter_generic_responses(response: str) -> str:
    """Filter out generic/cringe AI phrases and make responses punchier."""
    # Liste de phrases génériques à éviter (auto-congratulation)
    generic_phrases = [
        "je vais devoir ajouter",
        "ma liste de qualités",
        "ma longue liste",
        "quelqu'un doit bien le faire",
        "c'est mon travail",
        "je suis là pour",
        "mes capacités incroyables",
        "fantastique",
    ]
    
    # Si la réponse contient des phrases génériques, on la rejette (retourne vide)
    response_lower = response.lower()
    for phrase in generic_phrases:
        if phrase in response_lower:
            return ""  # Force un retry ou fallback
    
    return response


async def handle_chill_command(message: Message, config: dict, now):  # pylint: disable=unused-argument
    """Handle chill command with sarcastic AI responses for all users."""
    botname = config["bot"]["name"].lower()
    debug = config["bot"].get("debug", False)
    user = str(message.author.name or "user").lower()

    # Extraire le contenu du message sans le nom du bot
    raw_content = message.content or ""
    content = raw_content.strip().lower().replace(botname, "").strip()
    if not content:
        content = "Salut !"

    # Récupérer game/title depuis config (si disponible)
    game = config.get("stream", {}).get("game")
    title = config.get("stream", {}).get("title")

    # Construire le prompt avec make_prompt
    prompt = make_prompt(mode="chill", content=content, user=user, game=game, title=title)

    if debug:
        print(f"[CHILL] 📝 USER Prompt ({len(prompt)} chars): {prompt[:150]}{'...' if len(prompt) > 150 else ''}")

    response = await call_model(prompt, config, user=user, mode="chill")

    if debug:
        print(f"[CHILL] 📨 Réponse du modèle: {response[:100] if response else 'VIDE'}...")

    if not response:
        await message.channel.send("🤷 Réponse manquante.")
        return

    # Filtre anti-générique (garde la spontanéité du bot)
    filtered = filter_generic_responses(response.strip())
    if not filtered:
        if debug:
            print(f"[CHILL] ⚠️ Réponse générique filtrée: {response[:50]}...")
        filtered = "🤔 Hmm, laisse-moi réfléchir à ça..."

    # Sécurité Twitch (rare mais filet de sécurité)
    final_response = filtered if len(filtered) <= 500 else filtered[:497] + "…"
    
    try:
        if debug:
            print(f"[SEND] 📤 Envoi CHILL: {final_response[:100]}...")
        await message.channel.send(final_response)
        if debug:
            print(f"[CHILL] ✅ Réponse envoyée à @{user}")
    except Exception as e:
        print(f"[CHILL] ❌ Erreur d'envoi: {e}")

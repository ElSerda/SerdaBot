"""Command handler for chill/sarcastic bot responses."""

import random

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from cogs.roast_manager import load_roast_config, load_quotes_config, DEFAULT_PATH, QUOTES_PATH
from prompts.prompt_loader import make_prompt
from utils.model_utils import call_model


def truncate_response(response: str, limit: int = 500) -> str:
    """Truncates a response cleanly without cutting in the middle of a sentence."""
    if len(response) <= limit:
        return response
    best_dot = response[:limit].rfind(".")
    best_comma = response[:limit].rfind(",")
    if best_dot > 100:
        return response[: best_dot + 1].strip()
    elif best_comma > 100:
        return response[: best_comma + 1].strip()
    return response[:limit].strip() + "…"


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
    """Handle chill command with sarcastic AI responses."""
    botname = config["bot"]["name"].lower()
    debug = config["bot"].get("debug", False)
    user = str(message.author.name or "user").lower()

    # Extraire le contenu du message sans le nom du bot
    raw_content = message.content or ""
    content = raw_content.strip().lower().replace(botname, "").strip()
    if not content:
        content = "Salut !"

    # === ROAST DIRECT (100% pour users roast) ===
    roast_config = load_roast_config(DEFAULT_PATH)
    roast_users = {u.lower() for u in roast_config.get("users", [])}
    roast_quotes = roast_config.get("quotes", [])
    
    if user in roast_users and roast_quotes:
        # Envoyer roast direct sans passer par le modèle
        roast_quote = random.choice(roast_quotes)
        if debug:
            print(f"[CHILL] 🎭 ROAST DIRECT pour @{user}: {roast_quote}")
        await message.channel.send(roast_quote)
        return  # Exit early, pas de call au modèle

    # === QUOTE FUN (20% probabilité pour users normaux) ===
    quotes_config = load_quotes_config(QUOTES_PATH)
    fun_quotes = quotes_config.get("quotes", [])
    
    if fun_quotes and random.random() < 0.2:  # 20% chance
        fun_quote = random.choice(fun_quotes)
        if debug:
            print(f"[CHILL] 💬 QUOTE FUN pour @{user}: {fun_quote}")
        await message.channel.send(fun_quote)
        return  # Exit early, pas de call au modèle

    # === CHILL NORMAL (via modèle, 80% du temps) ===
    # Récupérer game/title depuis config (si disponible)
    game = config.get("stream", {}).get("game")
    title = config.get("stream", {}).get("title")

    # Construire le prompt avec make_prompt (gère automatiquement l'Easter Egg)
    prompt = make_prompt(mode="chill", content=content, user=user, game=game, title=title)

    if debug:
        print(f"[CHILL] 📝 USER Prompt ({len(prompt)} chars): {prompt[:150]}{'...' if len(prompt) > 150 else ''}")

    response = await call_model(prompt, config, user=user)

    if debug:
        print(f"[CHILL] 📨 Réponse du modèle: {response[:100] if response else 'VIDE'}...")

    if not response:
        await message.channel.send("🤷 Réponse manquante.")
        return

    # Filtre anti-générique
    filtered = filter_generic_responses(response.strip())
    if not filtered:
        if debug:
            print(f"[CHILL] ⚠️ Réponse générique filtrée: {response[:50]}...")
        # Fallback simple si la réponse est trop générique
        filtered = "🤔 Hmm, laisse-moi réfléchir à ça..."

    final = truncate_response(filtered)
    await message.channel.send(final)

    if debug:
        print(f"[CHILL] ✅ Réponse envoyée à @{user}")

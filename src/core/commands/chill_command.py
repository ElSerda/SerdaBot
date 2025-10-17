"""Command handler for chill/sarcastic bot responses."""

import os

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from prompts.prompt_loader import load_prompt_template
from utils.ask_utils import call_model


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
    lang = config["bot"].get("language", "fr")
    user = str(message.author.name or "user").lower()

    # Extraire le contenu du message sans le nom du bot
    raw_content = message.content or ""
    content = raw_content.strip().lower().replace(botname, "").strip()
    if not content:
        content = "Salut !"

    # Easter egg pour El_Serda uniquement
    try:
        if user in ["el_serda", "elserda"]:
            if debug:
                print(f"[CHILL] 🎉 Mode EASTER EGG activé pour {user}!")
            # Remonter de 2 niveaux: core/commands -> src, puis prompts/
            prompt_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'prompts'
            )
            easter_path = os.path.join(prompt_dir, 'prompt_chill_elserda.txt')
            with open(easter_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            prompt = prompt_template.replace("{message}", content)
            prompt = prompt.replace("{max_length}", "500")
        else:
            prompt_template = load_prompt_template("chill", lang)
            prompt = prompt_template.replace("{user}", user)
            prompt = prompt.replace("{max_length}", "500")
            prompt += f"\n\nMessage de {user}: {content}"
    except (FileNotFoundError, IOError, OSError) as e:
        print(f"[CHILL] ⚠️ Erreur chargement prompt: {e}")
        prompt = f"Réponds de manière détendue à {user}: {content}"
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

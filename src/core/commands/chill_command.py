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


async def handle_chill_command(message: Message, config: dict, now):  # pylint: disable=unused-argument
    """Handle chill command with sarcastic AI responses."""
    botname = config["bot"]["name"].lower()
    debug = config["bot"].get("debug", False)
    lang = config["bot"].get("language", "fr")
    user = str(message.author.name or "user").lower()

    # Extraire le contenu du message sans le nom du bot
    content = message.content.strip().lower().replace(botname, "").strip()
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

    final = truncate_response(response.strip())
    await message.channel.send(final)

    if debug:
        print(f"[CHILL] ✅ Réponse envoyée à @{user}")

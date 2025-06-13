
from datetime import datetime
from twitchio import Message
from utils.game_utils import (
    choose_best_summary,
    clean_summary,
    compress_platforms,
    fetch_game_data,
    fetch_steam_summary,
    normalize_platforms,
    sanitize_slug,
)
from utils.llm import clean_response


async def handle_game_command(message: Message, config: dict, game_name: str, now):
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)
    cooldown = config["bot"].get("cooldown", 60)

    if not await validate_game_name(message, game_name, user, debug):
        return

    await message.channel.send("🎮 Recherche du jeu...")
    try:
        data = await fetch_game_data(game_name, config)
        if not await handle_no_data(message, game_name, user, data, debug):
            return

        final_msg = await build_game_response(data, game_name, config, user, cooldown)
        await message.channel.send(final_msg)

        if debug:
            print(f"[GAME] ✅ Réponse envoyée : {final_msg}")
    except Exception as e:
        await message.channel.send(f"@{user} ⚠️ Erreur lors du traitement.")
        print(f"❌ [GAME] Exception : {e}")


async def validate_game_name(message, game_name, user, debug):
    if not game_name.strip():
        await message.channel.send(
            f"@{user} Tu as oublié de spécifier un jeu. Utilise la commande `!game nom_du_jeu`."
        )
        if debug:
            print(f"[GAME] ⚠️ Requête vide ignorée de @{user}")
        return False
    return True


async def handle_no_data(message, game_name, user, data, debug):
    if not data:
        await message.channel.send(f"❌ Jeu introuvable : {game_name}")
        if debug:
            print(f"[GAME] ❌ Aucun résultat pour '{game_name}'")
        return False
    return True


async def build_game_response(data, game_name, config, user, cooldown):
    name = data.get("name", "Inconnu")
    summary_raw = data.get("summary", "")
    slug = data.get("slug", "")
    igdb_url = f"https://www.igdb.com/games/{sanitize_slug(slug or name)}"

    if not summary_raw:
        return f"@{user} ⚠️ Ce jeu ne contient pas de résumé."

    summary_igdb = clean_summary(summary_raw, name)
    summary_steam = await fetch_steam_summary(name, config)
    summary, source, lang_igdb, lang_steam = await choose_best_summary(
        name, summary_igdb, summary_steam
    )

    platforms_list = normalize_platforms(data.get("platforms", []))
    platforms_list = compress_platforms(platforms_list)
    platforms_str = ", ".join(platforms_list) if platforms_list else "?"

    release_ts = data.get("first_release_date")
    release_date = (
        datetime.utcfromtimestamp(release_ts).strftime("%Y") if release_ts else "?"
    )

    base = f"@{user} 🎮 {name} ({release_date}, {platforms_str}) : "
    suffix = f" (voir + : {igdb_url}) (cooldown: {cooldown}s)"
    max_total = 500 - len(base) - len(suffix)

    raw = clean_response(summary)
    if len(raw) <= max_total:
        final_summary = raw
    else:
        cutoff = max_total
        best_dot = raw[:cutoff].rfind(".")
        best_comma = raw[:cutoff].rfind(",")
        if best_dot > 100:
            final_summary = raw[: best_dot + 1].strip()
        elif best_comma > 100:
            final_summary = raw[: best_comma + 1].strip()
        else:
            final_summary = raw[:cutoff].strip() + "…"

    print(f"[GAME] Source : {source}")
    print(f"[GAME] Langues détectées → IGDB: {lang_igdb}, Steam: {lang_steam}")
    print(f"[GAME] IGDB URL : {igdb_url}")

    return f"{base}{final_summary}{suffix}"

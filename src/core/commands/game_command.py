"""Command handler for game information lookup."""

import json
from datetime import datetime

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from utils.game_utils import (
    choose_best_summary,
    clean_summary,
    compress_platforms,
    fetch_game_data,
    fetch_steam_summary,
    normalize_platforms,
    sanitize_slug,
)
from utils.translator import Translator


def clean_translation(text: str) -> str:
    """Clean common translation mistakes in French game descriptions."""
    replacements = {
        "plateforme super étanche": "jeu de plateforme",
        "secrets dérisoires": "secrets cachés",
        "rassemble le mystère": "découvre les mystères",
        "défis réalisés à la main": "niveaux faits main",
        "ouvert-monde": "monde ouvert",
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    return text


async def handle_game_command(message: Message, config: dict, game_name: str, now):  # pylint: disable=unused-argument
    """Handle the !gameinfo command to fetch game information."""
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)
    cooldown = config["bot"].get("cooldown", 60)

    # Initialize translator
    translator = Translator()

    if not game_name.strip():
        await message.channel.send(
            f"@{user} Tu as oublié de spécifier un jeu. Utilise la commande `!game nom_du_jeu`."
        )
        if debug:
            print(f"[GAME] ⚠️ Requête vide ignorée de @{user}")
        return

    await message.channel.send("🎮 Recherche du jeu...")
    try:
        data = await fetch_game_data(game_name)

        if debug:
            debug_data = {k: v for k, v in data.items() if k != "summary"}
            print(
                "[GAME] 🔎 Données brutes API (hors summary) :\n"
                + json.dumps(debug_data, indent=2, ensure_ascii=False)
            )

        if not data:
            await message.channel.send(f"❌ Jeu introuvable : {game_name}")
            if debug:
                print(f"[GAME] ❌ Aucun résultat pour '{game_name}'")
            return

        name = data.get("name", "Inconnu")
        summary_raw = data.get("summary", "")
        slug = data.get("slug", "")
        igdb_url = f"https://www.igdb.com/games/{sanitize_slug(slug or name)}"

        summary_igdb = clean_summary(summary_raw, name)
        summary_steam = await fetch_steam_summary()
        summary, source, lang_igdb, lang_steam = await choose_best_summary(
            summary_igdb, summary_steam
        )

        # Simple language detection and translation using our translator
        translated = summary
        try:
            # If summary looks like English, translate it
            if any(
                word in summary.lower()
                for word in ['the', 'and', 'you', 'with', 'for', 'this', 'that']
            ):
                input_len = len(summary)
                input_tokens = input_len // 4  # Estimation: ~4 chars = 1 token
                print(f"[METRICS-GAME] 🌐 Traduction EN→FR: {input_len} chars (~{input_tokens} tokens)")

                result = translator.translate(summary, source='en', target='fr')
                if result and not result.startswith('⚠️'):  # Translation succeeded
                    translated = result
                    output_len = len(translated)
                    output_tokens = output_len // 4
                    print(f"[METRICS-GAME] ✅ Traduit: {output_len} chars (~{output_tokens} tokens)")
                else:
                    print("[METRICS-GAME] ⚠️ Traduction échouée, texte original conservé")
        except (RuntimeError, ValueError, KeyError) as e:
            if debug:
                print(f"[GAME] ⚠️ Translation error: {e}")

        translated = clean_translation(translated)

        # Gestion des dates
        release_ts = data.get("first_release_date")
        if not release_ts:
            release_dates = data.get("release_dates", [])
            if release_dates and isinstance(release_dates, list):
                for entry in release_dates:
                    if isinstance(entry, dict) and entry.get("date"):
                        release_ts = entry["date"]
                        break
        if not release_ts:
            release_ts = data.get("release")

        try:
            if release_ts is not None:
                release_ts = int(release_ts)
                release_year = datetime.utcfromtimestamp(release_ts).strftime('%Y')
            else:
                release_year = "?"
        except (ValueError, TypeError) as e:
            if debug:
                print(f"[GAME] ⚠️ Erreur date release_ts: {release_ts} → {e}")
            release_year = "?"

        if debug:
            print(f"[GAME] Date brute : {release_ts} → année : {release_year}")

        # Construction du message
        base = f"@{user} 🎮 {name}"
        base += f" ({release_year})" if release_year != "?" else "(date inconnue)"

        platforms = compress_platforms(normalize_platforms(data.get("platforms", [])))
        base += f", {', '.join(platforms)}" if platforms else ",plateformes inconnues"

        game_modes = data.get("game_modes", [])
        if not game_modes and "mode" in data:
            game_modes = [{"name": data["mode"]}]
        mode_display = ""
        if isinstance(game_modes, list):
            modes = []
            for mode in game_modes:
                name = mode.get("name", "") if isinstance(mode, dict) else str(mode)
                if "single" in name.lower():
                    modes.append("Solo")
                elif "multi" in name.lower():
                    modes.append("Multi")
            if modes:
                mode_display = " - " + ", ".join(sorted(set(modes)))

        suffix = f" ({igdb_url}) ({cooldown}s)"
        max_chars = 500 - len(base) - len(suffix) - len(mode_display) - 3 - 20

        if len(translated) > max_chars:
            cut_dot = translated[:max_chars].rfind(". ")
            cut_comma = translated[:max_chars].rfind(",")
            if cut_dot > 100:
                translated = translated[:cut_dot + 1].strip()
            elif cut_comma > 100:
                translated = translated[:cut_comma + 1].strip()
            else:
                translated = translated[:max_chars].strip() + "…"

        final = f"{base}{mode_display} :\n{translated}{suffix}"

        # Métriques finales
        final_len = len(final)
        final_tokens = final_len // 4
        print(f"[METRICS-GAME] 📤 Message final: {final_len} chars (~{final_tokens} tokens)")

        await message.channel.send(final)

        if debug:
            print(f"[GAME] ✅ Résumé source : {source}")
            print(f"[GAME] Langue IGDB: {lang_igdb}, Steam: {lang_steam}")
            print(f"[GAME] IGDB URL : {igdb_url}")
            print(f"[GAME] Plateformes : {platforms}")
            print(f"[GAME] Modes de jeu : {mode_display.strip(' -')}")

    except (RuntimeError, ValueError, KeyError, TypeError) as e:
        await message.channel.send(f"@{user} ⚠️ Erreur lors du traitement.")
        print(f"❌ [GAME] Exception : {e}")
